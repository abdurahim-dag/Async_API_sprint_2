import os
from contextlib import closing

import elasticsearch as es

from backoff import on_exception
from logger import logger
from models import LoadSettings


class Load:
    """Load to ES index."""
    def __init__(
        self,
        settings: LoadSettings,
    ):
        self.settings = settings

    def _create_index(self):
        """Create index if not found."""
        check = self.client.indices.exists(
            index=self.settings.index_name
        )
        if not check:
            with closing(
                    open(self.settings.schema_file_path, 'r', encoding='utf-8')
            ) as file:
                body = file.read()
                self.client.indices.create(
                    index=self.settings.index_name,
                    body=body,
                )
                logger.info("ES index created!")


    @on_exception(
        exception=es.exceptions.ElasticsearchException,
        start_sleep_time=1,
        factor=2,
        border_sleep_time=15,
        max_retries=15,
        logger=logger,
    )
    def load(self):
        """Load bulk batches rows to ES index."""
        self.client = es.Elasticsearch(
            self.settings.conn_str
        )
        self._create_index()

        for file_path in self.settings.transform_path.glob('**/*.json'):
            with closing(open(file_path, 'r', encoding='utf-8')) as file:
                body = file.read()
                self.client.bulk(
                    index=self.settings.index_name,
                    body=body,
                )
                logger.info('%s loaded to ES!', file.name)
            os.remove(file_path)
