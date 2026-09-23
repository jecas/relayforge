class RelayForgeError(Exception):
    status_code = 500
    code = "relayforge_error"
    message = "An unexpected error occurred."


class ProviderError(RelayForgeError):
    status_code = 502
    code = "provider_error"
    message = "The external provider returned an error."


class ProviderRequestError(ProviderError):
    status_code = 502
    code = "provider_request_error"
    message = "The provider rejected the request."


class ProviderAuthenticationError(ProviderError):
    status_code = 502
    code = "provider_authentication_error"
    message = "Provider authentication failed."


class ProviderNotFoundError(ProviderError):
    status_code = 404
    code = "provider_not_found"
    message = "The requested provider resource was not found."


class ProviderRateLimitError(ProviderError):
    status_code = 503
    code = "provider_rate_limited"
    message = "The provider rate limit was exceeded."


class ProviderUnavailableError(ProviderError):
    status_code = 503
    code = "provider_unavailable"
    message = "The provider is temporarily unavailable."


class ProviderTimeoutError(ProviderError):
    status_code = 504
    code = "provider_timeout"
    message = "The provider request timed out."


class ProviderProtocolError(ProviderError):
    status_code = 502
    code = "provider_protocol_error"
    message = "The provider returned an invalid response."
