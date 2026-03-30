.PHONY: build up down logs shell migrate makemigrations superuser collectstatic

build:
	docker-compose build

start:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

inside:
	docker container exec -it django_app bash

shell:
	docker-compose exec web uv run python manage.py shell

bash:
	docker-compose exec web bash

makemigrations:
	docker-compose exec web uv run python manage.py makemigrations

migrate:
	docker-compose exec web uv run python manage.py migrate

superuser:
	docker-compose exec web uv run python manage.py createsuperuser

collectstatic:
	docker-compose exec web uv run python manage.py collectstatic --noinput

reset-db:
	docker-compose down -v
	docker-compose up -d