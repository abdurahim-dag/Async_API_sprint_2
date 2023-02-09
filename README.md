# Проектная работа 5 спринта
https://github.com/abdurahim-dag/Async_API_sprint_2

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить во втором спринте модуля "Сервис Async API".

Сделайте функциональные тесты для вашего API, чтобы быть уверенными, что код работает правильно, а все функции отрабатывают корректно. Тесты должны запускаться как локально, так и через docker-compose.

Описание результата:

1. Напишите функциональные тесты в соответствии с приведённой в уроке структурой папок.
2. Напишите docker-compose-файл для запуска API, Elasticsearch, Redis и тестов.
3. Обязательно сделайте waiter для Elasticsearch и Redis.
4. Тесты должны быть написаны с использованием библиотек pytest и aiohttp.
5. Напишите функциональные тесты для метода  /search:
   - все граничные случаи по валидации данных;
   - вывести только N записей;
   - поиск записи или записей по фразе;
   - поиск с учётом кеша в Redis.
6. Напишите функциональные тесты для метода  /film:
   - все граничные случаи по валидации данных;
   - поиск конкретного фильма;
   - вывести все фильмы;
   - поиск с учётом кеша в Redis.
7. Напишите функциональные тесты для метода  /person:
   - все граничные случаи по валидации данных;
   - поиск конкретного человека;
   - поиск всех фильмов с участием человека;
   - вывести всех людей;
   - поиск с учётом кеша в Redis.
8. Напишите функциональные тесты для метода  /genre:
   - все граничные случаи по валидации данных;
   - поиск конкретного жанра;
   - вывести все жанры;
   - поиск с учётом кеша в Redis.

# Разработчики:
Рагим.

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
- .\tests: тесты ручек api.

# Компоненты приложения, описанные в Docker compose:
- db-movie: БД Postgres;
- app-movie: админка на Django;
- es01: ElasticSearch;
- etl: кастомный etl;
- fastapi: API приложения на fast;
- redis: сервер кэширования на Redis;
- nginx-movie: прокси сервер на Nginx;
- tests: докер образ, для тестирования.

# Сборка docker compose осуществляется из двух файлов:
   - для prod: docker-compose.yml, docker-compose.prod.yml;
   - для dev:  docker-compose.yml, docker-compose.override.yml;
   - для tests: docker-compose.yml, docker-compose.tests.yml;

# Порядок запуска dev (Windows 10):
1. Создаём .env.dev на сонове .env.example. Редактируем .env.dev подводя его к dev(APP_USER=root)
2. docker compose --env-file ./.env.dev up -d --no-deps --build
3. Если первый запуск, то одной командой в WSL: make windows-dev-post-start
4. Если надо сразу перенести данные PG в ES, а не ждать события ETL:
   - Войти в терминал docker etl-movie.
   - Запустить ETL в папке(CWD: /app) - /app/run.sh

# Порядок запуска prod:
1. make start-prod
2. Если надо сразу перенести данные PG в ES, а не ждать события ETL:
   - docker exec -it etl-movie bash -c "/app/run.sh" 
   При запуске не забыть указать env-file: env.prod(такой же как env.example).

# Порядок запуска tests:
1. Создаём .env.dev на сонове .env.example. Редактируем .env.dev подводя его к dev(APP_USER=root)
2. make start-tests
3. Смотрим лог контейнера.
4. docker compose down -v

# В случаи проблем при запуске Docker compose, добавьте --no-deps --build:
   - удалить образы и volumes;
   - docker compose --env-file ./.env.dev up -d --no-deps --build
   - docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file ./.env.prod up -d --no-deps --build
   - возможно при первом старте нужно использовать впн(есть ситуация при использовании впн возникает ошибка аутентификации в докер хаб, после создания некоторых образов, при такой ошибке отключаем впн и опять строим бразы)
