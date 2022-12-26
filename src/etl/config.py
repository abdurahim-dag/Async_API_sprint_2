import os
from pathlib import Path, PurePath

from models import (Environments, ExtractSettings, LoadSettings, TransformSettings,
                    Movie, Genre)


class Config:

    def __init__(
            self,
            environments: Environments,
            es_index,
            es_schema_file_name,
            sql_extract_file_name,
            model
    ):
        # Settings for PostgresExtractor.
        pg_conn_params = {
            'dbname': environments.pg_db_name,
            'user': environments.pg_user,
            'password': environments.pg_password,
            'host': environments.pg_host,
            'port': environments.pg_port,
        }
        pg_schema = environments.pg_schema
        batches = environments.batches
        pg_extract_dir = environments.extract_data_dir
        pg_extract_path = Path(pg_extract_dir)
        sql_dir = environments.sql_dir

        if not pg_extract_path.exists():
            os.mkdir(pg_extract_dir)
        sql_path = Path(
            PurePath(Path(sql_dir)),
        )
        if not sql_path.exists():
            raise FileExistsError(f"SQL DIR NOT EXISTS")
        sql_extract_file_path = Path(
            PurePath(
                sql_path,
                sql_extract_file_name
            )
        )
        if not sql_extract_file_path.exists():
            raise FileExistsError(f"SQL EXTRACT FILE NOT EXISTS")

        # Settings for DataTransform.
        transform_dir = environments.transform_data_dir
        transform_path = Path(transform_dir)
        if not transform_path.exists():
            os.mkdir(transform_dir)

        # Settings for ElasticsearchLoader.
        es_host = environments.es_host
        es_port = environments.es_port
        es_conn_str = f"http://{es_host}:{es_port}"

        es_settings_dir = environments.es_settings_path
        es_settings_path = Path(es_settings_dir)
        if not es_settings_path.exists():
            raise FileExistsError(f"ES SETTINGS DIR NOT EXISTS")

        es_schema_file_path = Path(
            PurePath(
                es_settings_path,
                es_schema_file_name
            )
        )
        if not es_schema_file_path.exists():
            raise FileExistsError(f"ES SCHEMA FILE NOT EXISTS")

        self.extract_settings = ExtractSettings(
            conn_params=pg_conn_params,
            schemas=pg_schema,
            extract_path=pg_extract_path,
            sql_file=sql_extract_file_path,
            batches=batches,
        )
        self.transform_settings = TransformSettings(
            transform_path=transform_path,
            extract_path=pg_extract_path,
            index_name=es_index,
            model=model,
        )
        self.load_settings = LoadSettings(
            conn_str=es_conn_str,
            index_name=es_index,
            transform_path=transform_path,
            schema_file_path=es_schema_file_path,
        )
