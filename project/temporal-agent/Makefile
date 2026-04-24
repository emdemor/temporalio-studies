COMPOSE := docker compose -f docker/docker-compose.yml

.PHONY: up down logs ps clean ui api workflow waiter-start waiter-stop waiter-logs help

help:
	@echo "Targets disponíveis:"
	@echo "  up     - Sobe todos os serviços em background"
	@echo "  down   - Para e remove os containers"
	@echo "  logs   - Segue os logs de todos os serviços"
	@echo "  ps     - Lista containers e status"
	@echo "  clean  - Remove containers, volumes e rede (reset completo)"
	@echo "  ui     - Abre o Temporal UI no browser"
	@echo "  api    - Abre o Swagger da API no browser"
	@echo "  workflow <rota> <arg>  - Chama uma rota da API (ex: make workflow greeting Josue)"
	@echo "  waiter-start <id>      - Inicia um WaiterWorkflow com o session id fornecido"
	@echo "  waiter-stop <id>       - Envia signal stop para encerrar o WaiterWorkflow"
	@echo "  waiter-logs            - Exibe só os logs do worker em tempo real"

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

clean:
	$(COMPOSE) down -v --remove-orphans

ui:
	xdg-open http://localhost:8080 2>/dev/null || open http://localhost:8080

api:
	xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs

workflow:
	curl -s -X POST http://localhost:8000/$(word 2,$(MAKECMDGOALS)) \
		-H "Content-Type: application/json" \
		-d '{"name": "$(word 3,$(MAKECMDGOALS))"}' | python3 -m json.tool

waiter-start:
	curl -s -X POST http://localhost:8000/waiter/$(word 2,$(MAKECMDGOALS))/start | python3 -m json.tool

waiter-stop:
	curl -s -X POST http://localhost:8000/waiter/$(word 2,$(MAKECMDGOALS))/stop | python3 -m json.tool

waiter-logs:
	$(COMPOSE) logs -f worker

%:
	@:
