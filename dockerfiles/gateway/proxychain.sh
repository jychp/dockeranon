#!/bin/sh
pproxy -v -l redir://0.0.0.0:8888 -r socks5://127.0.0.1:9050 &
