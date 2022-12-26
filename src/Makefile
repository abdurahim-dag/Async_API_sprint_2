1-django-migrate:
	docker exec -it app-movie python manage.py migrate
2-django-collstatic:
	docker exec -it app-movie python manage.py collectstatic --no-input
3-django-create-admin:
	docker exec -e DJANGO_SUPERUSER_USERNAME=admin \
                -e DJANGO_SUPERUSER_PASSWORD=1 \
                -e DJANGO_SUPERUSER_EMAIL=mail@mail.ru \
        -it app-movie python manage.py createsuperuser --noinput || true

4-load-sqlite:
	docker exec -it app-movie bash -c "cd /app; python -m sqlite_to_postgres.load_data"

5-pg-to-es:
	docker exec -it etl-movie bash -c "cd /app; python -m etl"

0-start-dev:
	docker compose --env-file ./.env.dev up -d --no-deps --build

0-start-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file ./.env.prod up -d

start-dev: 0-start-dev 1-django-migrate 3-django-create-admin 4-load-sqlite
start-prod: 0-start-prod 1-django-migrate 2-django-collstatic 3-django-create-admin 4-load-sqlite
windows-dev-post-start: 1-django-migrate 3-django-create-admin 4-load-sqlite