# Cesium Web Frontend

[![Build Status](https://travis-ci.org/cesium-ml/cesium_web.svg?branch=master)](https://travis-ci.org/cesium-ml/cesium_web)

## Running the app

Initialize the RethinkDB database with `make db_init`, start the server with
`make` and navigate to `localhost:5000` in a browser.


## Dev

`npm v^3.0.0` required.

Run `make` to install dependencies and launch the web server.

See the above section to run the app from here.

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
