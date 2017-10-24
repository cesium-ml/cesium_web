baselayer/README.md:
	git submodule update --init --remote
	$(MAKE) baselayer-update

.PHONY: baselayer-update
baselayer-update:
	./baselayer/tools/submodule_update.sh

log: baselayer/README.md
	make -C baselayer log

run: baselayer/README.md
	make -C baselayer run

run_testing: baselayer/README.md
	make -C baselayer run_testing

run_production: baselayer/README.md
	make -C baselayer run_production

test: baselayer/README.md
	make -C baselayer test

test_headless: baselayer/README.md
	make -C baselayer test_headless

db_init: baselayer/README.md
	make -C baselayer db_init

db_clear: baselayer/README.md
	make -C baselayer db_clear

docker-images:
	# Add --no-cache flag to rebuild from scratch
	docker build -t cesium/web . && docker push cesium/web
