#!/usr/bin/env bash

PLAT=$(uname)

if [[ $PLAT == 'Darwin' ]]; then
    echo "Configuring OSX postgres"
    createdb -w cesium
    createdb -w cesium_test
    createuser cesium
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium_test to cesium;'
else
    echo "Configuring Linux postgres"
    sudo -u postgres psql -c 'CREATE DATABASE cesium;'
    sudo -u postgres psql -c 'CREATE DATABASE cesium_test;'
    sudo -u postgres psql -c 'CREATE USER cesium;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium_test to cesium;'
fi

