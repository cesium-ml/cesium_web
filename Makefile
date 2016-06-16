SHELL = /bin/bash

.DEFAULT_GOAL := run_debug

db_init:
	-sudo -u postgres psql -c 'CREATE DATABASE cesium;'
	-sudo -u postgres psql -c 'CREATE USER cesium;'
	-sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'

db_init_force:
	./cesium_react_mock --db-init --force

run_debug:
	./cesium_react_mock --debug

run:
	./cesium_react_mock

bundle:
	webpack

install:
	npm install
