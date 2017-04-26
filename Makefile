SHELL = /bin/bash
SUPERVISORD=supervisord
SUPERVISORCTL=supervisorctl -c conf/supervisord_common.conf

.DEFAULT_GOAL := run

bundle = ./static/build/bundle.js
webpack = ./node_modules/.bin/webpack


dependencies:
	@./tools/silent_monitor.py pip install -r requirements.txt
	@./tools/silent_monitor.py ./tools/check_js_deps.sh

db_init:
	@./tools/silent_monitor.py ./tools/db_init.sh

db_clear:
	PYTHONPATH=. ./tools/db_clear.py

$(bundle): webpack.config.js package.json
	$(webpack)

bundle: $(bundle)

bundle-watch:
	$(webpack) -w

paths:
	@mkdir -p log run tmp
	@mkdir -p log/sv_child
	@mkdir -p ~/.local/cesium/logs

log: paths
	./tools/watch_logs.py

run: paths dependencies
	@echo "Supervisor will now fire up various micro-services."
	@echo
	@echo " - Please run \`make log\` in another terminal to view logs"
	@echo " - Press Ctrl-D to abort the server"
	@echo " - Type \`status\` too see microservice status"
	@echo
	@$(SUPERVISORD) -c conf/supervisord.conf &
	
	@echo "Entering supervisor control panel."
	@sleep 1 && $(SUPERVISORCTL) -i status
	
	@echo -n "Shutting down supervisord..."
	@$(SUPERVISORCTL) shutdown

# Attach to terminal of running webserver; useful to, e.g., use pdb
attach:
	$(SUPERVISORCTL) fg app

testrun:
	$(SUPERVISORD) -c conf/supervisord_testing.conf

clean:
	rm $(bundle)

test_headless: paths dependencies
	PYTHONPATH='.' xvfb-run ./tools/test_frontend.py

test: paths dependencies
	PYTHONPATH='.' ./tools/test_frontend.py

stop:
	$(SUPERVISORCTL) stop all

status:
	PYTHONPATH='.' ./tools/supervisor_status.py

docker-images:
	# Add --no-cache flag to rebuild from scratch
	docker build -t cesium/web . && docker push cesium/web

# Call this target to see which Javascript dependencies are not up to date
check-js-updates:
	./tools/check_js_updates.sh
