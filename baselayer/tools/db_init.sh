#!/usr/bin/env bash

PLAT=$(uname)

app_name=$1
user_name=$2

if [ "$app_name" == "" ]; then
    echo "ERROR - App/DB name was not supplied to db_init.sh"
    exit 1
fi

if [ "$user_name" == "" ]; then
    user_name=$app_name
fi


test_suffix='_test'
app_name_test=$app_name$test_suffix

if [[ $PLAT == 'Darwin' ]]; then
    echo "Configuring OSX postgres"
    createdb -w $app_name
    createdb -w $app_name_test
    createuser $user_name
    psql -U $user_name -c 'GRANT ALL PRIVILEGES ON DATABASE '$app_name' to '$user_name';'
    psql -U $user_name -c 'GRANT ALL PRIVILEGES ON DATABASE '$app_name_test' to '$user_name';'
else
    echo "Configuring Linux postgres"
    sudo -u postgres psql -c 'CREATE DATABASE '$app_name';'
    sudo -u postgres psql -c 'CREATE DATABASE '$app_name_test';'
    sudo -u postgres psql -c 'CREATE USER '$user_name';'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE '$app_name' to '$user_name';'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE '$app_name_test' to '$user_name';'
fi
