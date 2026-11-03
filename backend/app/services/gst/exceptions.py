from app.utils.exceptions import AppException

class GSTProviderError(AppException):
    def __init__(self, message: str = "GST Provider Error"):
        super().__init__(status_code=502, error_code="GST_PROVIDER_ERROR", message=message)

class GSTInvalidFormatError(AppException):
    def __init__(self, message: str = "Invalid GSTIN Format"):
        super().__init__(status_code=400, error_code="GST_INVALID_FORMAT", message=message)

class GSTNotFoundError(AppException):
    def __init__(self, message: str = "GSTIN Not Found"):
        super().__init__(status_code=404, error_code="GST_NOT_FOUND", message=message)

class GSTTimeoutError(AppException):
    def __init__(self, message: str = "GST Provider Timeout"):
        super().__init__(status_code=504, error_code="GST_TIMEOUT", message=message)
