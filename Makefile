.PHONY: help

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SHELL:=/bin/bash
workers=1

all: help

.PHONY:
help:
	@echo "Shipping Route Selector API development"
	@echo ""
	@echo "build                     Create the containers used in the development environment"
	@echo "tests                     Execute the tests in the development environment"
	@echo "run                       Starts application"
	@echo "run-with-worker           Starts application"
	@echo "clean                     Remove all application related containers"
	@echo ""

.PHONY:
build: clean
	@docker-compose -f docker/docker-compose.yml build --force-rm --pull taipy

.PHONY:
run: build
	@docker-compose -f docker/docker-compose.yml up -d taipy

.PHONY:
run-with-worker: build
	@docker-compose -f docker/docker-compose.yml -f docker/docker-compose-worker.yml up

.PHONY:
clean:
	@docker-compose -f docker/docker-compose.yml -f docker/docker-compose-worker.yml down
