"""Classes for handling HTTP Exceptions"""
from typing import Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request

# pylint: disable=unused-argument


class CustomHTTPException(Exception):
  """Exception raised for any API errors.
  Attributes:
    message -- explanation of the error
  """

  def __init__(self, status_code: int, success: bool, message: str, data: Any):
    self.status_code = status_code
    self.message = message
    self.success = success
    self.data = data
    super().__init__(message)


# Exception handlers
def add_exception_handlers(app: FastAPI):

  @app.exception_handler(CustomHTTPException)
  async def generic_exception_handler(req: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": exc.data
        })

  @app.exception_handler(RequestValidationError)
  async def pydantic_exception_handler(req: Request,
                                       exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Failed",
            "data": exc.errors()
        })

class InvalidToken(CustomHTTPException):
  """Exception raised when permission is denied.
  Request is not authenticated due to missing,
  invalid or expired OAuth token.
  Attributes:
    message -- explanation of the error
  """

  def __init__(self, message: str = "Unauthenticated"):
    super().__init__(status_code=498, message=message, success=False, data=None)

class ResourceNotFound(CustomHTTPException):
  """Exception raised if a Resource is not found.
  A specific resource is not found.
  Attributes:
    message -- explanation of the error
  """

  def __init__(self, message: str = "Resource Not Found"):
    super().__init__(status_code=404, message=message, \
      success=False, data=None)

class InternalServerError(CustomHTTPException):
  """Exception raised for errors caused by the server.
  Errors caused at the server end which may require manual intervention.
  This includes the following:
    Data Loss: In case there is an unrecoverable data loss because of request.
    Unknown: An error occurred because of unknown reasons.
    Internal: An error occurred because of a server bug.
  Attributes:
    message -- explanation of the error
  """

  def __init__(self, message: Any = "Internal Server Error"):
    super().__init__(status_code=500, message=message, \
      success=False, data=None)
class Conflict(CustomHTTPException):
  """Exception raised for conflicts.
  Conflict of the request with current system state.
  This can include the following:
    Aborted: Concurrency conflict. Read-modify-write conflict.
    Already exists:The resource that a client tried to create already exists.
  Attributes:
    message -- explanation of the error
  """

  def __init__(self, message: Any = "Conflict"):
    super().__init__(status_code=409, message=message, \
      success=False, data=None)
