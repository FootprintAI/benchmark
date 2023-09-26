#!/usr/bin/env bash
#
#
if [ $# -eq 0 ]
  then
    echo "need haproxy.cfg"
    exit
fi

echo "running with cfg: $(pwd)/$1"

docker run --restart=always -d --network host \
   -v $(pwd)/$1:/usr/local/etc/haproxy/haproxy.cfg:ro \
   haproxytech/haproxy-alpine:2.3.2
