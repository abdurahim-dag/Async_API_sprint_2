"""
Основной модуль выгрузки, трансформирования и загрузки данных
 из БД sqlite в БД Postgres.
"""
import os
from pathlib import Path
from pathlib import PurePath

from dotenv import load_dotenv

from sqlite_to_postgres.extract import Extract
from sqlite_to_postgres.load import Load
from sqlite_to_postgres.map_tables import map_tables
from sqlite_to_postgres.transform import Transform
from sqlite_to_postgres.utils import file_rename

if __name__ == "__main__":
    load_dotenv()

    data_dir = os.environ.get('DATA_DIR', '.data')
    data_path = Path(
        PurePath(Path(data_dir)),
    )
    if not data_path.exists():
        raise FileExistsError(f"SQLITE DATA DIR NOT EXISTS")

    db_sqlite = os.environ.get('SQLITE_DB_PATH', 'db.sqlite')
    db_sqlite_path = Path(
        PurePath(Path(data_dir)),
        db_sqlite,
    )
    if not db_sqlite_path.exists():
        raise FileExistsError(f"FILE SQLITE DB NOT EXISTS")

    extract_filename = os.environ.get('EXTRACT_FILE_NAME', 'extract.csv')
    upload_filename = os.environ.get('UPLOAD_FILE_NAME', 'upload.csv')
    conn_params = {
        'drivername': 'postgresql+psycopg2',
        'database': os.environ.get('PG_DB_NAME', 'postgres'),
        'username': os.environ.get('PG_USER', 'postgres'),
        'password': os.environ.get('PG_PASSWORD', 'postgres'),
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': os.environ.get('PG_PORT', 'postgres'),
    }
    schema = os.environ.get('PG_SCHEMA', 'public')

    extract = Extract(db_sqlite, data_path)
    transform = Transform(data_path)
    load = Load(conn_params, schema, data_path)

    for table in map_tables:
        table_name = table[0]
        dataclass_target = table[1]
        dataclass_source = table[2]

        extracted_filename = file_rename(extract_filename, table_name)
        extract.extract(table_name, dataclass_source, extracted_filename)

        upload_file_name = file_rename(upload_filename, table_name)
        transform.transform(extracted_filename, upload_file_name, dataclass_target)

        load.upload(upload_file_name, table_name)
