from typing import Any, Dict, Optional


def error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format a standard error response."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }


def success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """Format a standard success response."""
    response: Dict[str, Any] = {"data": data}
    if message:
        response["message"] = message
    return response
