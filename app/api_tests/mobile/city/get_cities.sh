#!/usr/bin/env bash
source ../host.sh
# route
ROUTE=cities/

http GET ${BASE_URL}${ROUTE} \
    -A jwt -a $(cat ../token.txt): -v

