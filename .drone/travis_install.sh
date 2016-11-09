#!/bin/bash

set -ex


section "install.base.requirements"
pip install --upgrade pip
hash -d pip  # find upgraded pip
pip install --retries 3 -q requests
section_end "install.base.requirements"


section "install.cesium.requirements"
pip install --retries 3 -r requirements.txt
pip list
section_end "install.cesium.requirements"


section "install.cesium_web.requirements"
sudo ln -s /usr/bin/nodejs /usr/bin/node
npm --version
node --version
make dependencies
section_end "install.cesium_web.requirements"


section "init.cesium_web"
make paths
make db_init
make db_test_data
make bundle
section_end "init.cesium_web"


section "install.chromedriver"
wget http://chromedriver.storage.googleapis.com/2.23/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip chromedriver -d /usr/local/bin
rm chromedriver_linux64.zip
which chromium-browser
chromium-browser --version
section_end "install.chromedriver"
