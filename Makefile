SHELL = /bin/bash

.DEFAULT_GOAL := run_debug

db_init:
	./cesium_react_mock --db-init

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
