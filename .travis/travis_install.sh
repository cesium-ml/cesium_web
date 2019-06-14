#!/bin/bash

set -ex

section "install.base.requirements"

# Check Firefox version
firefox --version

# Install v1.7 or newer of nginx to support 'if' statement for logging
sudo apt-add-repository -y ppa:nginx/stable
sudo apt update
sudo apt install -y nginx

pip install --upgrade pip
hash -d pip  # find upgraded pip
section_end "install.base.requirements"

section "install.cesium_web.requirements"
npm -g install npm@latest
npm --version
node --version

if [[ ${TRIGGERED_FROM_REPO} == "cesium-ml/cesium" ]]; then
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


section "init.db"
make db_init
section_end "init.db"


section "install.geckodriver.and.selenium"
wget https://github.com/mozilla/geckodriver/releases/download/v0.20.0/geckodriver-v0.20.0-linux64.tar.gz
sudo tar -xzf geckodriver-v0.20.0-linux64.tar.gz -C /usr/local/bin
rm geckodriver-v0.20.0-linux64.tar.gz
which geckodriver
geckodriver --version
pip install --upgrade selenium
python -c "import selenium; print(f'Selenium {selenium.__version__}')"
section_end "install.geckodriver.and.selenium"
