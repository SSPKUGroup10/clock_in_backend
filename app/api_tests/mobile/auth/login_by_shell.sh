#!/usr/bin/env bash

touch ../token.txt
./login.sh $1 \
    | grep -o '"accessToken": [^, }]*' | sed 's/^.*: //' | sed -e 's/^"//'  -e 's/"$//' > ../token.txt
cat ../token.txt
