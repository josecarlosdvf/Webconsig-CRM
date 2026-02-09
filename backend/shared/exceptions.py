"""Standardized exceptions."""

from fastapi import HTTPException


def not_found(message: str) -> HTTPException:
	"""Return a 404 Not Found exception."""
	return HTTPException(status_code=404, detail=message)


def conflict(message: str) -> HTTPException:
	"""Return a 409 Conflict exception."""
	return HTTPException(status_code=409, detail=message)


def forbidden(message: str) -> HTTPException:
	"""Return a 403 Forbidden exception."""
	return HTTPException(status_code=403, detail=message)


def validation_error(message: str) -> HTTPException:
	"""Return a 422 Unprocessable Entity exception."""
	return HTTPException(status_code=422, detail=message)


def unauthorized(message: str) -> HTTPException:
	"""Return a 401 Unauthorized exception."""
	return HTTPException(status_code=401, detail=message)

