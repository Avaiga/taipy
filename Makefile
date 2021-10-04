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
	@echo "run-multiple              Starts application"
	@echo "clean                     Remove all application related containers"
	@echo ""

.PHONY:
build: clean
	@docker-compose build --force-rm --pull taipy

.PHONY:
run: build
	@docker-compose up -d taipy

.PHONY:
run-multiple: build
	@docker-compose up -d --scale taipy=$(workers) nginx

.PHONY:
clean:
	@docker-compose down
