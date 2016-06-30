SHELL = /bin/bash
SUPERVISORD=supervisord

.DEFAULT_GOAL := run

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


$(bundle): webpack.config.js
	$(webpack)

bundle: $(bundle)

bundle-watch:
	$(webpack) -w

$(node):
	npm install

paths:
	mkdir -p log run tmp
	mkdir -p log/sv_child
	mkdir -p ~/.local/cesium/logs

log: paths
	./tools/watch_logs.py

run: paths dependencies
	$(SUPERVISORD) -c conf/supervisord.conf

debug:
	$(SUPERVISORD) -c conf/supervisord_debug.conf

# Attach to terminal of running webserver; useful to, e.g., use pdb
attach:
	supervisorctl -c conf/supervisord_common.conf fg flask

clean:
	rm $(bundle)
