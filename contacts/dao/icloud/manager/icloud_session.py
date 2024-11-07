"""An iCloud browsing session."""
from __future__ import annotations

import http.cookiejar as cookielib
import inspect
import json
import logging
from typing import NoReturn, cast

import requests

from contacts.dao import icloud
from contacts.dao.icloud.manager import exception

LOGGER = logging.getLogger(__name__)

HEADER_DATA = {
    "X-Apple-ID-Account-Country": "account_country",
    "X-Apple-ID-Session-Id": "session_id",
    "X-Apple-Session-Token": "session_token",
    "X-Apple-TwoSV-Trust-Token": "trust_token",
    "X-Apple-I-Rscd": "apple_rscd",
    "X-Apple-I-Ercd": "apple_ercd",
    "scnt": "scnt",
}


class ICloudSession(requests.Session):
    """iCloud session."""

    def __init__(self, manager: icloud.manager.ICloudManager, path: str) -> None:
        super().__init__()

        LOGGER.debug("Using session file %s" % path)

        self.data = {}
        self.path = path
        self.manager = manager
        self.cookies: cookielib.LWPCookieJar | None = None  # type: ignore

        try:
            with open(path) as file:
                self.data = json.load(file)
        except FileNotFoundError:
            LOGGER.debug("Session file does not exist")
        if client_id := self.data.get("client_id"):
            self.client_id = client_id
        else:
            self.data.update({"client_id": self.manager.client_id})

    def request(  # type: ignore
        self, method: str | bytes, url: str | bytes, **kwargs
    ) -> requests.Response:
        # Change logging to the right manager endpoint
        callee = inspect.stack()[2]
        module = inspect.getmodule(callee[0])
        request_logger = logging.getLogger(
            module.__name__ if module is not None else ""
        ).getChild("http")
        if self.manager.password_filter not in request_logger.filters:
            request_logger.addFilter(self.manager.password_filter)

        request_logger.debug("%r %r %s" % (method, url, kwargs.get("data", "")))

        has_retried = kwargs.get("retried")
        kwargs.pop("retried", None)
        response = super().request(method, url, **kwargs)

        content_type = response.headers.get("Content-Type", "").split(";")[0]
        json_mimetypes = ["application/json", "text/json"]

        for header in HEADER_DATA:
            if response.headers.get(header):
                session_arg = HEADER_DATA[header]
                self.data.update(
                    {session_arg: response.headers.get(header)}
                )

        # Save session_data to file
        with open(self.path, "w") as outfile:
            json.dump(self.data, outfile)
            LOGGER.debug("Saved session data to file")

        # Save cookies to file
        cast(cookielib.LWPCookieJar, self.cookies).save(
            ignore_discard=True, ignore_expires=True
        )
        LOGGER.debug("Cookies saved to %s", self.manager.cookiejar_path)

        if not response.ok and (
            content_type not in json_mimetypes
            or response.status_code in [421, 450, 500]
        ):
            try:
                fmip_url = self.manager.get_webservice_url("findme")
                if (
                    has_retried is None
                    and response.status_code == 450
                    and fmip_url in url
                ):
                    # Handle re-authentication for Find My iPhone
                    LOGGER.debug("Re-authenticating Find My iPhone manager")
                    try:
                        self.manager.authenticate(True, "find")
                    except exception.ICloudAPIResponseException:
                        LOGGER.debug("Re-authentication failed")
                    kwargs["retried"] = True
                    return self.request(method, url, **kwargs)
            except Exception:
                pass

            if has_retried is None and response.status_code in [421, 450, 500]:
                api_error = exception.ICloudAPIResponseException(
                    response.reason, response.status_code, retry=True
                )
                request_logger.debug(api_error)
                kwargs["retried"] = True
                return self.request(method, url, **kwargs)

            self._raise_error(response.status_code, response.reason)

        if content_type not in json_mimetypes:
            return response

        try:
            data = response.json()
        except requests.JSONDecodeError:
            request_logger.warning("Failed to parse response with JSON mimetype")
            return response

        request_logger.debug(data)

        if isinstance(data, dict):
            reason = data.get("errorMessage")
            reason = reason or data.get("reason")
            reason = reason or data.get("errorReason")
            if not reason and isinstance(data.get("error"), str):
                reason = data.get("error")
            if not reason and data.get("error"):
                reason = "Unknown reason"

            code = data.get("errorCode")
            if not code and data.get("serverErrorCode"):
                code = data.get("serverErrorCode")

            if reason:
                self._raise_error(code, reason)

        return response

    def _raise_error(self, code: int | str | None, reason: str) -> NoReturn:
        if (
            self.manager.requires_2sa
            and reason == "Missing X-APPLE-WEBAUTH-TOKEN cookie"
        ):
            raise exception.ICloud2SARequiredException(self.manager.user["accountName"])
        if code in ("ZONE_NOT_FOUND", "AUTHENTICATION_FAILED"):
            reason = (
                "Please log into https://icloud.com/ to manually "
                "finish setting up your iCloud manager"
            )
            api_error: exception.ICloudException = (
                exception.ICloudServiceNotActivatedException(reason, code)
            )
            LOGGER.error(api_error)

            raise api_error
        if code == "ACCESS_DENIED":
            reason = (
                reason + ".  Please wait a few minutes then try again."
                "The remote servers might be trying to throttle requests."
            )
        if code in [421, 450, 500]:
            reason = "Authentication required for Account."

        api_error = exception.ICloudAPIResponseException(reason, code)
        LOGGER.error(api_error)
        raise api_error
