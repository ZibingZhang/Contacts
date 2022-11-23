"""Manage an iCloud session."""
import getpass
import http.cookiejar as cookielib
import inspect
import json
import logging
import os
import re
import tempfile
import uuid
from typing import Text

import requests

from data.icloud.exceptions import (
    ICloud2SARequiredException,
    ICloudAPIResponseException,
    ICloudFailedLoginException,
    ICloudServiceNotActivatedException,
)

LOGGER = logging.getLogger(__name__)

HEADER_DATA = {
    "X-Apple-ID-Account-Country": "account_country",
    "X-Apple-ID-Session-Id": "session_id",
    "X-Apple-Session-Token": "session_token",
    "X-Apple-TwoSV-Trust-Token": "trust_token",
    "scnt": "scnt",
}


class ICloudSessionManager:
    """
    A base authentication class for the iCloud manager. Handles the
    authentication required to access iCloud services.

    Usage:
        import ICloudSessionManager
        session = ICloudSessionManager('username@icloud.com', 'password')
        session.contacts.get_contacts_and_groups()
    """

    AUTH_ENDPOINT = "https://idmsa.apple.com/appleauth/auth"
    HOME_ENDPOINT = "https://www.icloud.com"
    SETUP_ENDPOINT = "https://setup.icloud.com/setup/ws/1"

    def __init__(
        self,
        apple_id: str,
        password: str,
        cookie_directory: str | None = None,
        verify: bool = True,
        client_id: str | None = None,
        with_family: bool = True,
    ) -> None:
        self.user = {"accountName": apple_id, "password": password}
        self.data = {}
        self.params = {}
        self.client_id = client_id or ("auth-%s" % str(uuid.uuid1()).lower())
        self.with_family = with_family

        self.password_filter = _PasswordFilter(password)
        LOGGER.addFilter(self.password_filter)

        if cookie_directory:
            self._cookie_directory = os.path.expanduser(
                os.path.normpath(cookie_directory)
            )
            if not os.path.exists(self._cookie_directory):
                os.mkdir(self._cookie_directory, 0o700)
        else:
            topdir = os.path.join(tempfile.gettempdir(), "pyicloud")
            self._cookie_directory = os.path.join(topdir, getpass.getuser())
            if not os.path.exists(topdir):
                os.mkdir(topdir, 0o777)
            if not os.path.exists(self._cookie_directory):
                os.mkdir(self._cookie_directory, 0o700)

        LOGGER.debug("Using session file %s" % self.session_path)

        self.session_data = {}
        try:
            with open(self.session_path) as session_f:
                self.session_data = json.load(session_f)
        except Exception:
            LOGGER.info("Session file does not exist")
        if self.session_data.get("client_id"):
            self.client_id = self.session_data.get("client_id")
        else:
            self.session_data.update({"client_id": self.client_id})

        self.session = _ICloudSession(self)
        self.session.verify = verify
        self.session.headers.update(
            {"Origin": self.HOME_ENDPOINT, "Referer": "%s/" % self.HOME_ENDPOINT}
        )

        cookiejar_path = self.cookiejar_path
        self.session.cookies = cookielib.LWPCookieJar(filename=cookiejar_path)
        if os.path.exists(cookiejar_path):
            try:
                self.session.cookies.load(ignore_discard=True, ignore_expires=True)
                LOGGER.debug("Read cookies from %s" % cookiejar_path)
            except Exception:
                # Most likely a pickled cookiejar from earlier versions.
                # The cookiejar will get replaced with a valid one after
                # successful authentication.
                LOGGER.warning("Failed to read cookiejar %s" % cookiejar_path)

        self._webservices = None
        self.authenticate()

    @property
    def cookiejar_path(self) -> str:
        """Get path for cookiejar file."""
        return os.path.join(
            self._cookie_directory,
            "".join([c for c in self.user.get("accountName") if re.match(r"\w", c)]),
        )

    @property
    def session_path(self) -> str:
        """Get path for session data file."""
        return os.path.join(
            self._cookie_directory,
            "".join([c for c in self.user.get("accountName") if re.match(r"\w", c)])
            + ".session",
        )

    @property
    def requires_2sa(self) -> bool:
        """Returns True if two-step authentication is required."""
        return self.data.get("dsInfo", {}).get("hsaVersion", 0) >= 1 and (
            self.data.get("hsaChallengeRequired", False) or not self.is_trusted_session
        )

    @property
    def requires_2fa(self) -> bool:
        """Returns True if two-factor authentication is required."""
        return self.data["dsInfo"].get("hsaVersion", 0) == 2 and (
            self.data.get("hsaChallengeRequired", False) or not self.is_trusted_session
        )

    @property
    def is_trusted_session(self) -> bool:
        """Returns True if the session is trusted."""
        return self.data.get("hsaTrustedBrowser", False)

    @property
    def trusted_devices(self) -> dict:
        """Returns devices trusted for two-step authentication."""
        request = self.session.get(
            "%s/listDevices" % self.SETUP_ENDPOINT, params=self.params
        )
        return request.json().get("devices")

    def login(self) -> None:
        if self.requires_2fa:
            print("Two-factor authentication required.")
            code = input(
                "Enter the code you received of one of your approved devices: "
            )
            result = self.validate_2fa_code(code)
            print("Code validation result: %s" % result)

            if not result:
                raise ICloudFailedLoginException("Failed to verify security code")

            if not self.is_trusted_session:
                print("Session is not trusted. Requesting trust...")
                result = self.trust_session()
                print("Session trust result %s" % result)

                if not result:
                    print(
                        "Failed to request trust. You will likely be prompted for the"
                        " code again in the coming weeks"
                    )
        elif self.requires_2sa:
            print("Two-step authentication required. Your trusted devices are:")

            devices = self.trusted_devices
            for i, device in enumerate(devices):
                print(
                    "  %s: %s"
                    % (
                        i,
                        device.get(
                            "deviceName", "SMS to %s" % device.get("phoneNumber")
                        ),
                    )
                )

            device = input("Which device would you like to use?")
            device = devices[device]
            if not self.send_verification_code(device):
                raise ICloudFailedLoginException("Failed to send verification code")

            code = input("Please enter validation code")
            if not self.validate_verification_code(device, code):
                raise ICloudFailedLoginException("Failed to verify verification code")

    def authenticate(
        self, force_refresh: bool = False, service: str | None = None
    ) -> None:
        """
        Handles authentication, and persists cookies so that
        subsequent logins will not cause additional e-mails from Apple.
        """
        login_successful = False
        if self.session_data.get("session_token") and not force_refresh:
            LOGGER.debug("Checking session token validity")
            try:
                self.data = self._validate_token()
                login_successful = True
            except ICloudAPIResponseException:
                LOGGER.debug("Invalid authentication token, will log in from scratch.")

        if not login_successful and service is not None:
            app = self.data["apps"][service]
            if (
                "canLaunchWithOneFactor" in app
                and app["canLaunchWithOneFactor"] is True
            ):
                LOGGER.debug(
                    "Authenticating as %s for %s" % (self.user["accountName"], service)
                )
                try:
                    self._authenticate_with_credentials_service(service)
                    login_successful = True
                except Exception:
                    LOGGER.debug(
                        "Could not log into manager. Attempting brand new login."
                    )

        if not login_successful:
            LOGGER.debug("Authenticating as %s" % self.user["accountName"])

            data = dict(self.user)

            data["rememberMe"] = True
            data["trustTokens"] = []
            if self.session_data.get("trust_token"):
                data["trustTokens"] = [self.session_data.get("trust_token")]

            headers = self._get_auth_headers()

            if self.session_data.get("scnt"):
                headers["scnt"] = self.session_data.get("scnt")

            if self.session_data.get("session_id"):
                headers["X-Apple-ID-Session-Id"] = self.session_data.get("session_id")

            try:
                self.session.post(
                    "%s/signin" % self.AUTH_ENDPOINT,
                    params={"isRememberMeEnabled": "true"},
                    data=json.dumps(data),
                    headers=headers,
                )
            except ICloudAPIResponseException as error:
                msg = "Invalid email/password combination."
                raise ICloudFailedLoginException(msg, error)

            self._authenticate_with_token()

        self._webservices = self.data["webservices"]

        LOGGER.debug("Authentication completed successfully")

    def _authenticate_with_token(self) -> None:
        """Authenticate using session token."""
        data = {
            "accountCountryCode": self.session_data.get("account_country"),
            "dsWebAuthToken": self.session_data.get("session_token"),
            "extended_login": True,
            "trustToken": self.session_data.get("trust_token", ""),
        }

        try:
            req = self.session.post(
                "%s/accountLogin" % self.SETUP_ENDPOINT, data=json.dumps(data)
            )
            self.data = req.json()
        except ICloudAPIResponseException as error:
            msg = "Invalid authentication token."
            raise ICloudFailedLoginException(msg, error)

    def _authenticate_with_credentials_service(self, service: str) -> None:
        """Authenticate to a specific manager using credentials."""
        data = {
            "appName": service,
            "apple_id": self.user["accountName"],
            "password": self.user["password"],
        }

        try:
            self.session.post(
                "%s/accountLogin" % self.SETUP_ENDPOINT, data=json.dumps(data)
            )

            self.data = self._validate_token()
        except ICloudAPIResponseException as error:
            msg = "Invalid email/password combination."
            raise ICloudFailedLoginException(msg, error)

    def _validate_token(self) -> dict:
        """Checks if the current access token is still valid."""
        LOGGER.debug("Checking session token validity")
        try:
            req = self.session.post("%s/validate" % self.SETUP_ENDPOINT, data="null")
            LOGGER.debug("Session token is still valid")
            return req.json()
        except ICloudAPIResponseException as err:
            LOGGER.debug("Invalid authentication token")
            raise err

    def _get_auth_headers(self, overrides=None) -> dict[str, str]:
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Apple-OAuth-Client-Id": (
                "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d"
            ),
            "X-Apple-OAuth-Client-Type": "firstPartyAuth",
            "X-Apple-OAuth-Redirect-URI": "https://www.icloud.com",
            "X-Apple-OAuth-Require-Grant-Code": "true",
            "X-Apple-OAuth-Response-Mode": "web_message",
            "X-Apple-OAuth-Response-Type": "code",
            "X-Apple-OAuth-State": self.client_id,
            "X-Apple-Widget-Key": (
                "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d"
            ),
        }
        if overrides:
            headers.update(overrides)
        return headers

    def send_verification_code(self, device: dict) -> bool:
        """Requests that a verification code is sent to the given device."""
        data = json.dumps(device)
        request = self.session.post(
            "%s/sendVerificationCode" % self.SETUP_ENDPOINT,
            params=self.params,
            data=data,
        )
        return request.json().get("success", False)

    def validate_verification_code(self, device: dict, code: str) -> bool:
        """Verifies a verification code received on a trusted device."""
        device.update({"verificationCode": code, "trustBrowser": True})
        data = json.dumps(device)

        try:
            self.session.post(
                "%s/validateVerificationCode" % self.SETUP_ENDPOINT,
                params=self.params,
                data=data,
            )
        except ICloudAPIResponseException as error:
            if error.code == -21669:
                # Wrong verification code
                return False
            raise

        self.trust_session()

        return not self.requires_2sa

    def validate_2fa_code(self, code: str) -> bool:
        """Verifies a verification code received via Apple's 2FA system (HSA2)."""
        data = {"securityCode": {"code": code}}

        headers = self._get_auth_headers({"Accept": "application/json"})

        if self.session_data.get("scnt"):
            headers["scnt"] = self.session_data.get("scnt")

        if self.session_data.get("session_id"):
            headers["X-Apple-ID-Session-Id"] = self.session_data.get("session_id")

        try:
            self.session.post(
                "%s/verify/trusteddevice/securitycode" % self.AUTH_ENDPOINT,
                data=json.dumps(data),
                headers=headers,
            )
        except ICloudAPIResponseException as error:
            if error.code == -21669:
                # Wrong verification code
                LOGGER.error("Code verification failed.")
                return False
            raise

        LOGGER.debug("Code verification successful.")

        self.trust_session()
        return not self.requires_2sa

    def trust_session(self) -> bool:
        """Request session trust to avoid user log in going forward."""
        headers = self._get_auth_headers()

        if self.session_data.get("scnt"):
            headers["scnt"] = self.session_data.get("scnt")

        if self.session_data.get("session_id"):
            headers["X-Apple-ID-Session-Id"] = self.session_data.get("session_id")

        try:
            self.session.get(
                "%s/2sv/trust" % self.AUTH_ENDPOINT,
                headers=headers,
            )
            self._authenticate_with_token()
            return True
        except ICloudAPIResponseException:
            LOGGER.error("Session trust failed.")
            return False

    def get_webservice_url(self, ws_key: str) -> str:
        """Get webservice URL, raise an exception if not exists."""
        if self._webservices.get(ws_key) is None:
            raise ICloudServiceNotActivatedException("Webservice not available", ws_key)
        return self._webservices[ws_key]["url"]

    def __unicode__(self) -> str:
        return "iCloud API: %s" % self.user.get("accountName")

    def __str__(self) -> str:
        as_unicode = self.__unicode__()
        return as_unicode

    def __repr__(self) -> str:
        return "<%s>" % str(self)


class _ICloudSession(requests.Session):
    """iCloud session."""

    def __init__(self, manager: ICloudSessionManager) -> None:
        self.manager = manager
        requests.Session.__init__(self)

    def request(
        self, method: str, url: str | bytes | Text, **kwargs
    ) -> requests.Response:
        # Change logging to the right manager endpoint
        callee = inspect.stack()[2]
        module = inspect.getmodule(callee[0])
        request_logger = logging.getLogger(module.__name__).getChild("http")
        if self.manager.password_filter not in request_logger.filters:
            request_logger.addFilter(self.manager.password_filter)

        request_logger.debug("%s %s %s" % (method, url, kwargs.get("data", "")))

        has_retried = kwargs.get("retried")
        kwargs.pop("retried", None)
        response = super(_ICloudSession, self).request(method, url, **kwargs)

        content_type = response.headers.get("Content-Type", "").split(";")[0]
        json_mimetypes = ["application/json", "text/json"]

        for header in HEADER_DATA:
            if response.headers.get(header):
                session_arg = HEADER_DATA[header]
                self.manager.session_data.update(
                    {session_arg: response.headers.get(header)}
                )

        # Save session_data to file
        with open(self.manager.session_path, "w") as outfile:
            json.dump(self.manager.session_data, outfile)
            LOGGER.debug("Saved session data to file")

        # Save cookies to file
        self.cookies.save(ignore_discard=True, ignore_expires=True)
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
                    except ICloudAPIResponseException:
                        LOGGER.debug("Re-authentication failed")
                    kwargs["retried"] = True
                    return self.request(method, url, **kwargs)
            except Exception:
                pass

            if has_retried is None and response.status_code in [421, 450, 500]:
                api_error = ICloudAPIResponseException(
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
        except Exception:
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

    def _raise_error(self, code: int, reason: str) -> None:
        if (
            self.manager.requires_2sa
            and reason == "Missing X-APPLE-WEBAUTH-TOKEN cookie"
        ):
            raise ICloud2SARequiredException(self.manager.user["apple_id"])
        if code in ("ZONE_NOT_FOUND", "AUTHENTICATION_FAILED"):
            reason = (
                "Please log into https://icloud.com/ to manually "
                "finish setting up your iCloud manager"
            )
            api_error = ICloudServiceNotActivatedException(reason, code)
            LOGGER.error(api_error)

            raise api_error
        if code == "ACCESS_DENIED":
            reason = (
                reason + ".  Please wait a few minutes then try again."
                "The remote servers might be trying to throttle requests."
            )
        if code in [421, 450, 500]:
            reason = "Authentication required for Account."

        api_error = ICloudAPIResponseException(reason, code)
        LOGGER.error(api_error)
        raise api_error


class _PasswordFilter(logging.Filter):
    """Password log hider."""

    def __init__(self, password: str) -> None:
        super().__init__(password)

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if self.name in message:
            record.msg = message.replace(self.name, "*" * 8)
            record.args = []

        return True
