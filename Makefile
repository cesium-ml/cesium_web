baselayer/README.md:
	git submodule update --init --remote
	$(MAKE) baselayer-update

.PHONY: baselayer-update
baselayer-update:
	./baselayer/tools/submodule_update.sh

log:
	make -C baselayer log

run:
	make -C baselayer run

run_testing:
	make -C baselayer run_testing

run_production:
	make -C baselayer run_production

test_headless:
	make -C baselayer paths dependencies
	PYTHONPATH='.' xvfb-run baselayer/tools/test_frontend.py

test:
	make -C baselayer paths dependencies
	PYTHONPATH='.' baselayer/tools/test_frontend.py

docker-images:
	# Add --no-cache flag to rebuild from scratch
	docker build -t cesium/web . && docker push cesium/web
