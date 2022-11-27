"""iCloud exceptions."""


class ICloudException(Exception):
    """Generic iCloud exception."""


class ICloudAPIResponseException(ICloudException):
    """iCloud response exception."""

    def __init__(
        self, reason: str, code: int | str | None = None, retry: bool = False
    ) -> None:
        self.reason = reason
        self.code = code
        message = reason or ""
        if code:
            message += " (%s)" % code
        if retry:
            message += ". Retrying ..."

        super().__init__(message)


class ICloudServiceNotActivatedException(ICloudAPIResponseException):
    """iCloud manager not activated exception."""


class ICloudFailedLoginException(ICloudException):
    """iCloud failed login exception."""


class ICloud2SARequiredException(ICloudException):
    """iCloud 2SA required exception."""

    def __init__(self, apple_id: str) -> None:
        message = "Two-step authentication required for account: %s" % apple_id
        super().__init__(message)
