.DEFAULT_GOAL := run

-include baselayer/Makefile  # always clone baselayer if it doesn't exist

baselayer/Makefile:
	git submodule update --init --remote

docker-images:
	# Add --no-cache flag to rebuild from scratch
	docker build -t cesium/web . && docker push cesium/web
