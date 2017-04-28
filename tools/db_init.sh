#!/usr/bin/env bash

PLAT=$(uname)

# Travis-CI and Docker doesn't have sudo, so check if it's available
if [[ -x $(which sudo) ]]; then
    SUDO="sudo -u postgres"
else
    SUDO=""
fi

if [[ $PLAT == 'Darwin' ]]; then
    echo "Configuring OSX postgres"
    createdb -w cesium
    createdb -w cesium_test
    createuser cesium
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium_test to cesium;'
else
    echo "Configuring Linux postgres"
    $SUDO psql -c 'CREATE DATABASE cesium;'
    $SUDO psql -c 'CREATE DATABASE cesium_test;'
    $SUDO psql -c 'CREATE USER cesium;'
    $SUDO psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
    $SUDO psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium_test to cesium;'
fi

