from functional.utils.backoff import on_exception
from functional.utils.logger import logger


@on_exception(
    exception=Exception,
    start_sleep_time=1,
    factor=2,
    border_sleep_time=15,
    max_retries=15,
    logger=logger,
)
async def check(client):
    status = await client.ping()
    if not status:
        raise Exception('DB is not ready!')
