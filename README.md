# Cesium Web Frontend

[![Build Status](https://travis-ci.org/cesium-ml/cesium_web.svg?branch=master)](https://travis-ci.org/cesium-ml/cesium_web)

## Getting started

The easiest way to try the web app is to run it through docker:

1. Download the docker-compose file for Cesium:
   `curl -Lo docker-compose.yml http://bit.ly/29GkVXY`

2. Ensure you have Docker Compose up and running, then:
   `docker-compose up`

3. Wait a few seconds and navigate to
   http://localhost:9000

4. Create a project and go! If you want some test data, the header file is

   ```
   curl -Lo example-headers.dat http://bit.ly/29FtRXy
   ```

   and the time series data is

   ```
   curl -Lo example-series.tar.gz http://bit.ly/29HKmVZ
   ```

## Running the app on your local machine

1. Install the following dependencies:

- supervisor
- nginx
- postgresql (including libpq-dev on Debian)
- npm
- HDF5 and NetCDF4 headers, if available on your platform

On Debian, e.g., install these packages:

```
nginx supervisor postgresql libpq-dev npm nodejs-legacy libhdf5-dev libnetcdf-dev libpython3-dev
```

2. Install Python dependencies: `pip install -r requirements.txt`

3. Configurate database permissions for postgresql.  In your `pg_hba.conf`
   (typically located in `/etc/postgresql/9.5/main`):

Underneath the line

```
local   all             postgres                                peer
```

insert

```
local cesium cesium trust
local cesium_test cesium trust
```

Restart postgres (on Debian: `sudo service postgresql restart`)

4. Initialize the database with `make db_init`

5. Start the server with `make` and navigate to `localhost:5000` in a browser.

## Dev

1. `npm v^3.0.0` required.
2. Run `make` to launch the web server.

To execute the test suite:

- Install ChromeDriver from:
  https://sites.google.com/a/chromium.org/chromedriver/home

  (The binary has to be placed somewhere on your path.)

- Install Chrome or Chromium

- Optional: install xfvb for headless tests (only available on Linux)

- `make test_headless` or `make test`

## Dev tips

- Run `make log` to watch log output
- Run `make debug` to start webserver in debug mode
- Run `make attach` to attach to output of webserver; you can then set pdb
  traces for interactive access:

    import pdb; pdb.set_trace()

- To ensure that JavaScript & JSX code conforms with industry style
  recommendations, after adding or modifying any .js or .jsx files, run ESLint with
  `node_modules/eslint/bin/eslint.js -c .eslintrc --ext .jsx,.js public/scripts/`.
  To automatically run ESLint when you make changes to your JavaScript code, add
  a pre-commit hook by adding the following to your .git/hooks/pre-commit :

```
#!/bin/bash
# Pre-commit Git hook to run ESLint on JavaScript files.
#
# If you absolutely must commit without testing,
# use: git commit --no-verify (git commit -n)

filenames=($(git diff --cached --name-only HEAD))

for i in "${filenames[@]}"
do
    if [[ $i =~ \.js$ ]] || [[ $i =~ \.jsx$ ]] ;
    then
        echo node_modules/eslint/bin/eslint.js -c .eslintrc $i
        node_modules/eslint/bin/eslint.js -c .eslintrc $i
        if [ $? -ne 0 ];
        then
            exit 1
        fi
    fi
done
```

- Run `make docker-images` to build and push to Docker hub
