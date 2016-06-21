#!/usr/bin/env bash

id -u postgres

if [[ $? == 0 ]]; then
    echo "Configuring Linux postgres"
    sudo -u postgres psql -c 'CREATE DATABASE cesium;'
    sudo -u postgres psql -c 'CREATE USER cesium;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
else
    echo "Configuring OSX postgres"
    createdb -w cesium
    createuser cesium
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
fi
