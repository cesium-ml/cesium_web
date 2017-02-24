SHELL = /bin/bash
SUPERVISORD=supervisord

.DEFAULT_GOAL := run

bundle = ./public/build/bundle.js
webpack = ./node_modules/.bin/webpack


dev_dependencies:
	@./tools/install_deps.py requirements.dev.txt

dependencies:
	@./tools/install_deps.py requirements.txt
	npm update

db_init:
	./tools/db_create.sh

db_drop:
	PYTHONPATH=. ./tools/db_drop.py

db_test_data:
	PYTHONPATH=. python ./cesium_app/models.py

$(bundle): webpack.config.js package.json
	$(webpack)

bundle: $(bundle)

bundle-watch:
	$(webpack) -w

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
	supervisorctl -c conf/supervisord_common.conf fg app

clean:
	rm $(bundle)

test_headless: paths dependencies
	PYTHONPATH='.' xvfb-run ./tools/frontend_tests.py

test: paths dependencies
	PYTHONPATH='.' ./tools/frontend_tests.py

status:
	PYTHONPATH='.' ./tools/supervisor_status.py

docker-images:
	# Add --no-cache flag to rebuild from scratch
	docker build -t cesium/web . && docker push cesium/web
	cd docker/postgres && docker build -t cesium/postgres . && docker push cesium/postgres

npm-update:
	npm install -g npm-check-updates
	ncu
