class DemoClientError(Exception):
    """
    Base exception for known demo API-client failures.
    """


class DemoConnectionError(DemoClientError):
    """
    The frontend could not successfully communicate with the API.
    """


class DemoAPIError(DemoClientError):
    """
    The API returned an HTTP error response.
    """

    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        error_code: str | None = None,
    ):
        super().__init__(message)

        self.status_code = status_code
        self.error_code = error_code


class DemoProtocolError(DemoClientError):
    """
    The API response did not satisfy the response contract
    expected by the demo client.
    """

class DemoInputError(Exception):
    """
    Uploaded demo input cannot be converted into the
    API request representation.
    """