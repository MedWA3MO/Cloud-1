# Define variables
DOCKER_COMPOSE_FILE = srcs/docker-compose.yml
MARIADB_VOLUME_DIR = /opt/inception/data/mariadb
WP_VOLUME_DIR = /opt/inception/data/wordpress

all: up

up:
	mkdir -p $(MARIADB_VOLUME_DIR)
	mkdir -p $(WP_VOLUME_DIR)
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build -d

down:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

clean: down
	@docker rm $$(docker ps -a -q) 2>/dev/null || true
	@docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@docker network rm $$(docker network ls -q) 2>/dev/null || true


fclean: clean
	@docker rmi $$(docker images -q) 2>/dev/null || true

.PHONY: all up down clean fclean

