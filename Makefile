.PHONY: setup up down shell logs restart build

COURSE_REPO = https://github.com/temporalio/edu-101-python-code

setup:
	@if [ -d workspace/.git ]; then \
		echo "workspace ja foi clonado. Use 'git pull' dentro de workspace/ para atualizar."; \
	else \
		rm -f workspace/.gitkeep && git clone $(COURSE_REPO) workspace; \
	fi

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

shell:
	docker compose exec app bash

logs:
	docker compose logs -f

restart:
	docker compose restart app
