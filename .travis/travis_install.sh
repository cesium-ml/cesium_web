#!/bin/bash

set -ex

section "install.base.requirements"

# Install v1.7 or newer of nginx to support 'if' statement for logging
sudo apt-add-repository -y ppa:nginx/development
sudo apt update
sudo apt install -y nginx

pip install --upgrade pip
hash -d pip  # find upgraded pip
section_end "install.base.requirements"

section "install.cesium_web.requirements"
npm -g install npm@latest
npm --version
node --version
make dependencies
make check-js-updates

if [[ -n ${TRIGGERED_FROM_REPO} ]]; then
    mkdir cesium-clone
    cd cesium-clone
    git init
    git remote add origin git://github.com/${TRIGGERED_FROM_REPO}
    git fetch --depth=1 origin ${TRIGGERED_FROM_BRANCH}
    git checkout -b ${TRIGGERED_FROM_BRANCH} ${TRIGGERED_FROM_SHA}
    pip install .
    cd ..
fi

pip list --format=columns
section_end "install.cesium_web.requirements"


section "init.cesium_web"
make paths
make db_init
make bundle
section_end "init.cesium_web"


section "install.chromedriver"
wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip chromedriver -d /usr/local/bin
rm chromedriver_linux64.zip
which chromium-browser
chromium-browser --version
section_end "install.chromedriver"
