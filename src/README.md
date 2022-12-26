# Проектная работа 4 спринта
https://github.com/abdurahim-dag/Async_API_sprint_1

В папке **tasks** задачи, которые необходимо выполнить.

# Разработчики:
Рагим, Николай(BityutskiyNA), Даниил(TRUEVORO).

# Структура приложения наружу:
- Админка: http://localhost/admin
- Api: - http://localhost/api
- Openapi документация: http://127.0.0.1/api/openapi

# Структура приложения:
- .\app: админка приложения на Django;
- .\app\sqlite_to_postgres: etl переноса инициализирующих данных нашего приложения;
- .\db: образ Postgres и начальная схема БД;
- .\etl: etl переноса с периодичностью БД Postgres в индексы ES;
- .\fastapi-solution: задание текущего спринта, api для приложения написанное на fastapi и слой кэширования на Redis;
- .\nginx: образ и настройки прокси сервера nginx. 

# Компоненты приложения, описанные в Docker compose:
- db-movie: БД Postgres;
- app-movie: админка на Django;
- es01: ElasticSearch;
- etl: кастомный etl;
- fastapi: API приложения на fast;
- redis: сервер кэширования на Redis;
- nginx-movie: прокси сервер на Nginx.

# Порядок запуска dev (Windows 10):
1. docker compose --env-file ./.env.dev up -d --no-deps --build
2. Если первый запуск, то одной командой в WSL: make windows-dev-post-start
3. Если надо сразу перенести данные PG в ES, а не ждать события ETL:
   - Войти в терминал docker etl-movie.
   - Запустить ETL в папке(CWD: /app) - /app/run.sh

# Порядок запуска prod:
1. make start-prod
2. Если надо сразу перенести данные PG в ES, а не ждать события ETL:
   - Войти в терминал docker etl-movie.
   - Запустить ETL в папке(CWD: /app) - /app/run.sh
При запуске не забыть указать env-file: env.prod(такой же как env.example).

# В случаи проблем при запуске Docker compose, добавьте --no-deps --build:
   - docker compose --env-file ./.env.dev up -d --no-deps --build
   - docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file ./.env.prod up -d --no-deps --build