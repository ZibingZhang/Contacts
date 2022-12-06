"""General iCloud api wrapper."""
from __future__ import annotations

import functools
import getpass
import http.cookiejar as cookielib
import json
import logging
import os.path
import re
import tempfile
import uuid

from common import decorator
from dao import icloud
from dao.icloud._manager import exception

LOGGER = logging.getLogger(__name__)


class ICloudManager:
    """A base authentication class for the iCloud manager.

    Handles the authentication required to access iCloud services.
    """

    AUTH_ENDPOINT = "https://idmsa.apple.com/appleauth/auth"
    HOME_ENDPOINT = "https://www.icloud.com"
    SETUP_ENDPOINT = "https://setup.icloud.com/setup/ws/1"

    def __init__(
        self,
        apple_id: str | None = None,
        password: str | None = None,
        cookie_directory: str | None = None,
        verify: bool = True,
        client_id: str | None = None,
        with_family: bool = True,
    ) -> None:
        if apple_id is None or password is None:
            raise ValueError(
                "'apple_id' and 'password' required for initial instantiation"
            )

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
        except FileNotFoundError:
            LOGGER.debug("Session file does not exist")
        if self.session_data.get("client_id"):
            self.client_id = self.session_data.get("client_id")
        else:
            self.session_data.update({"client_id": self.client_id})

        self.session = icloud._manager.ICloudSession(self)
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
            except FileNotFoundError | ValueError:
                # Most likely a pickled cookiejar from earlier versions.
                # The cookiejar will get replaced with a valid one after
                # successful authentication.
                LOGGER.warning("Failed to read cookiejar %s" % cookiejar_path)

        self._webservices = None
        self.authenticate()

    @functools.cached_property
    def contact_manager(self) -> icloud._manager.ICloudContactManager:
        return icloud._manager.ICloudContactManager(self)

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

    @decorator.run_once
    def login(self) -> None:
        if self.requires_2fa:
            print("Two-factor authentication required.")
            code = input(
                "Enter the code you received of one of your approved devices: "
            )
            result = self._validate_2fa_code(code)
            print("Code validation result: %s" % result)

            if not result:
                raise exception.ICloudFailedLoginException(
                    "Failed to verify security code"
                )

            if not self.is_trusted_session:
                print("Session is not trusted. Requesting trust...")
                result = self._trust_session()
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
            if not self._send_verification_code(device):
                raise exception.ICloudFailedLoginException(
                    "Failed to send verification code"
                )

            code = input("Please enter validation code")
            if not self._validate_verification_code(device, code):
                raise exception.ICloudFailedLoginException(
                    "Failed to verify verification code"
                )

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
            except exception.ICloudAPIResponseException:
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
                except exception.ICloudFailedLoginException:
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
            except exception.ICloudAPIResponseException as error:
                msg = "Invalid email/password combination."
                raise exception.ICloudFailedLoginException(msg, error)

            self._authenticate_with_token()

        self._webservices = self.data["webservices"]

        LOGGER.debug("Authentication completed successfully")

    def get_webservice_url(self, ws_key: str) -> str:
        """Get webservice URL, raise an exception if not exists."""
        if self._webservices.get(ws_key) is None:
            raise exception.ICloudServiceNotActivatedException(
                "Webservice not available", ws_key
            )
        return self._webservices[ws_key]["url"]

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
        except exception.ICloudAPIResponseException as error:
            msg = "Invalid authentication token."
            raise exception.ICloudFailedLoginException(msg, error)

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
        except exception.ICloudAPIResponseException as error:
            msg = "Invalid email/password combination."
            raise exception.ICloudFailedLoginException(msg, error)

    def _validate_token(self) -> dict:
        """Checks if the current access token is still valid."""
        LOGGER.debug("Checking session token validity")
        try:
            req = self.session.post("%s/validate" % self.SETUP_ENDPOINT, data="null")
            LOGGER.debug("Session token is still valid")
            return req.json()
        except exception.ICloudAPIResponseException as err:
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

    def _send_verification_code(self, device: dict) -> bool:
        """Requests that a verification code is sent to the given device."""
        data = json.dumps(device)
        request = self.session.post(
            "%s/sendVerificationCode" % self.SETUP_ENDPOINT,
            params=self.params,
            data=data,
        )
        return request.json().get("success", False)

    def _validate_verification_code(self, device: dict, code: str) -> bool:
        """Verifies a verification code received on a trusted device."""
        device.update({"verificationCode": code, "trustBrowser": True})
        data = json.dumps(device)

        try:
            self.session.post(
                "%s/validateVerificationCode" % self.SETUP_ENDPOINT,
                params=self.params,
                data=data,
            )
        except exception.ICloudAPIResponseException as error:
            if error.code == -21669:
                # Wrong verification code
                return False
            raise

        self._trust_session()

        return not self.requires_2sa

    def _validate_2fa_code(self, code: str) -> bool:
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
        except exception.ICloudAPIResponseException as error:
            if error.code == -21669:
                # Wrong verification code
                LOGGER.error("Code verification failed.")
                return False
            raise

        LOGGER.debug("Code verification successful.")

        self._trust_session()
        return not self.requires_2sa

    def _trust_session(self) -> bool:
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
        except exception.ICloudAPIResponseException:
            LOGGER.error("Session trust failed.")
            return False


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
