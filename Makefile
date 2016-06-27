SHELL = /bin/bash

.DEFAULT_GOAL := run_debug

bundle = ./public/build/bundle.js
webpack = ./node_modules/.bin/webpack
node = ./node_modules/redux

dev_dependencies:
	@./tools/install_deps.py requirements.dev.txt

dependencies: $(node)
	@./tools/install_deps.py requirements.txt

db_init:
	-./tools/create_db.sh

db_init_force:
	./cesium_launcher --db-init --force

run_debug: dev_dependencies dependencies
	@echo "Launching webpack & dev web server..."
	@sh -c '$(webpack) -w & ./cesium_launcher --debug'

run: $(bundle) dependencies
	./cesium_launcher

$(bundle): webpack.config.js
	$(webpack)

bundle: $(bundle)

bundle-watch:
	$(webpack) -w

$(node):
	npm install

clean:
	rm $(bundle)
