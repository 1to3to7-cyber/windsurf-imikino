from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

class APIResponse:
    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {
            "success": True,
            "data": data,
            "message": message
        }
    
    @staticmethod
    def error(message: str, code: Optional[str] = None, field: Optional[str] = None) -> Dict[str, Any]:
        response = {
            "success": False,
            "error": {
                "message": message
            }
        }
        if code:
            response["error"]["code"] = code
        if field:
            response["error"]["field"] = field
        return response
    
    @staticmethod
    def not_found(resource: str = "Resource") -> Dict[str, Any]:
        return APIResponse.error(f"{resource} not found", "NOT_FOUND")
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized access") -> Dict[str, Any]:
        return APIResponse.error(message, "UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message: str = "Access denied") -> Dict[str, Any]:
        return APIResponse.error(message, "FORBIDDEN")
    
    @staticmethod
    def validation_error(message: str, field: str = None) -> Dict[str, Any]:
        return APIResponse.error(message, "VALIDATION_ERROR", field)
    
    @staticmethod
    def server_error(message: str = "Internal server error") -> Dict[str, Any]:
        return APIResponse.error(message, "SERVER_ERROR")

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        content=APIResponse.success(data, message),
        status_code=status_code
    )

def error_response(message: str, status_code: int = 400, code: Optional[str] = None, field: Optional[str] = None) -> JSONResponse:
    return JSONResponse(
        content=APIResponse.error(message, code, field),
        status_code=status_code
    )

def not_found_response(resource: str = "Resource") -> JSONResponse:
    return JSONResponse(
        content=APIResponse.not_found(resource),
        status_code=404
    )

def unauthorized_response(message: str = "Unauthorized access") -> JSONResponse:
    return JSONResponse(
        content=APIResponse.unauthorized(message),
        status_code=401
    )

def forbidden_response(message: str = "Access denied") -> JSONResponse:
    return JSONResponse(
        content=APIResponse.forbidden(message),
        status_code=403
    )

def validation_error_response(message: str, field: str = None) -> JSONResponse:
    return JSONResponse(
        content=APIResponse.validation_error(message, field),
        status_code=422
    )

def server_error_response(message: str = "Internal server error") -> JSONResponse:
    return JSONResponse(
        content=APIResponse.server_error(message),
        status_code=500
    )
