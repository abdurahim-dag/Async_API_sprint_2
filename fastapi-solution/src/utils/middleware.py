from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .babel import active_translation


class LocalizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == 'GET':
            active_translation(request.headers.get("accept-language", None))
        response = await call_next(request)
        return response
