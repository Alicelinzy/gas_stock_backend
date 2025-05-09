from rest_framework import status
from typing import Dict, Any, Optional

class RepositoryResponse:
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        message: str = "",
        status_code: int = status.HTTP_200_OK
    ):
        self.success = success
        self.data = data
        self.message = message
        self.status_code = status_code

class APIResponse:
    @staticmethod
    def success(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
        return {
            "success": True,
            "data": data,
            "message": message
        }

    @staticmethod
    def error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Dict[str, Any]:
        return {
            "success": False,
            "error": message,
            "status_code": status_code
        }