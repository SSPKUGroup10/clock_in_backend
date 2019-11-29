#!/usr/bin/env bash
source ../host.sh
# route
ROUTE=auth/wechat
echo ${BASE_URL}${ROUTE}

code=$1

http POST ${BASE_URL}${ROUTE} \
        code=${code} -v
