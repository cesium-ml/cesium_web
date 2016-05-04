SHELL = /bin/bash

.DEFAULT_GOAL := run_server_debug

db_init:
	./cesium_react_mock --db-init

db_init_force:
	./cesium_react_mock --db-init --force

run_server_debug:
	./cesium_react_mock --debug

run_server:
	./cesium_react_mock
