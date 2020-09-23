#!/bin/sh
mkdir ~/.ssh
chmod 700 ~/.ssh
/usr/bin/tor -f /etc/tor/torrc
echo "nameserver $GATEWAY_IP" > /etc/resolv.conf
# Wait for network connection
test=$(ip link show eth1)
while [ "$test" = "" ]; do
  sleep 1
  test=$(ip link show eth1)
done
python3 /root/webui/webui.py
