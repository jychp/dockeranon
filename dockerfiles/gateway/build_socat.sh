#!/bin/sh
echo "[*] Build socat"
echo "    install dependencies"
apk add --no-cache gcc git make autoconf musl-dev readline-dev openssl-dev linux-headers
apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing yodl
echo "    pulling sources"
git clone https://github.com/runsisi/socat
cd socat || exit 1
echo "    configure"
autoconf
./configure
make
make install
