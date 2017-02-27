#!/bin/bash

set -e

CHECKER=./node_modules/.bin/ncu

if [[ ! -x ${CHECKER} ]]; then
    npm install npm-check-updates > /dev/null 2>&1
fi

${CHECKER}

