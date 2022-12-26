import inspect
import pickle
from functools import wraps
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.concurrency import run_in_threadpool

import db.redis as redis


CACHE_EXPIRE_IN_SECONDS = 20 * 1


def cache(
        ttl: int = CACHE_EXPIRE_IN_SECONDS,
):
    """
    Cache for Operation on Redis.
    """
    def wrapper(func: Callable):

        # Если в сигнатуре функции не объявлен Request.
        # То добавим наш.
        signature = inspect.signature(func)
        request_param = next(
            (param for param in signature.parameters.values() if param.annotation is Request),
            None,
        )
        response_param = next(
            (param for param in signature.parameters.values() if param.annotation is Response),
            None,
        )
        parameters = [*signature.parameters.values()]
        if not request_param:
            parameters.append(
                inspect.Parameter(
                    name="request",
                    annotation=Request,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                ),
            )
        if not response_param:
            parameters.append(
                inspect.Parameter(
                    name="response",
                    annotation=Response,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                ),
            )
        if parameters:
            signature = signature.replace(parameters=parameters)
        func.__signature__ = signature

        @wraps(func)
        async def inner(*args, **kwargs):
            async def exec_func(*args, **kwargs):
                if inspect.iscoroutinefunction(func):
                    # Если функция асинхронная.
                    return await func(*args, **kwargs)
                else:
                    # Если функция синхронная.
                    return await run_in_threadpool(func, *args, **kwargs)

            # Забираем request и response.
            request: Optional[Request]
            response: Optional[Response]
            # И восстановим kwargs оригинальной функции.
            kwargs_origin = kwargs.copy()
            if not request_param:
                request = kwargs_origin.pop("request")
            else:
                request = kwargs_origin.get("request")
            if not response_param:
                response = kwargs_origin.pop("response")
            else:
                response = kwargs_origin.get("response")

            res = None
            if request:
                cache_control = request.headers.get("Cache-Control")
                if cache_control in ("no-store", "no-cache") or \
                   request.method != "GET":
                    res = await exec_func(*args, **kwargs_origin)
                else:
                    cache_key = str(request.url)
                    client = await redis.get_redis()
                    cache_value = await client.get(cache_key)
                    if cache_value:
                        res = pickle.loads(cache_value)
                    else:
                        res = await exec_func(*args, **kwargs_origin)
                        await client.set(cache_key, pickle.dumps(res))

                    # Чем больше запросов на cache_key, тем дольше он в кэше.
                    await client.expire(cache_key, ttl)

                    if response:
                        response.headers["Cache-Control"] = f"max-age={ttl}"

            return res
        return inner
    return wrapper

