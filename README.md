DockerAnon
==========

# General
Create 2 docker container (gateway + workstation) to ensure all traffic is anonymous.

By default only tor is launched on the gateway but you can configure multiple proxy, routes and DNS entry.

Workstation can be used with VNC (and noVNC in your navigator).

# Installation
## Requirements
You will need docker and a user allowed to use docker (you can use sudo or put your user in docker group).

You can use noVCN, but for convinience consider a VNC client, such as xtightvncviewer.

DockerAnon use python3 and some requirements (docker, prompt-toolkit, pyyaml, requests)

```bash
sudo apt install xtightvncviewer
sudo python3 -m pip install -r requirements.txt
```

## Configuration
DockerAnon use two config files 'config.yaml' and 'gateway.yaml'.

### config.yaml
This file contains containers configuration
* **NETWORK_NAME** *(dockeranon_net)*: Network name in Docker
* **NETWORK_RANGE** *(192.168.5.0/24*: Network range in Docker
* **GATEWAY_NAME** *(dockeranon_gateway)*: Gateway image name in Docker
* **GATEWAY_IP** *(192.168.5.254)*: Gateway IP (in network range)
* **GATEWAY_HOSTNAME** *(gateway)*: Gateway hostname
* **WORKSTATION_IMAGE** *(jychp/xubuntu:latest)*: DockerHub base image for workstation
* **WORKSTATION_NAME** *(dockeranon_workstation)*: Workstation image name in Docker
* **WORKSTATION_IP** *(192.168.5.10)*: Workstation IP (in network range)
* **WORKSTATION_RESOLUTION** *(1024x768)*: Workstation VNC screen resolution
* **WORKSTATION_PASSWD** *(password)*: VNC password (user password is resu)
* **WORKSTATION_APPS** *(empty)*: Workstation packages list (coma separated)
* **WORKSTATION_HOSTNAME** *(ubuntu)*: Workstation hostname
* **VNC_CLIENT** *(/usr/bin/vncviewer)*: VNC client path (could be empty)
* **MOUNT_POINT** *(/dev/shm/dockeranon)*: Path of share directory (between host and workstation)
* **MOUNT_POINT_USE** *(True)*: Choose to mount share directory

### gateway.yaml
This file contains proxy list, routes and dns custom entry for gateway:
```yaml
PROXIES:                          # List of proxies
  tor:
    type: tor
  ssh_1:                          # Proxy name
    type: ssh                     # Proxy type (tor, ssh, socks5, socks4, http, httponly, ss, ssr)
    host: 1.2.3.4                 # Proxy/SSH host
    port: 22                      # Proxy/SSH port
    user: jychp                   # Proxy/SSH user
    password: password            # Proxy/SSH password
    key: ""                       # SSH private key base64 encoded (cat id_rsa|base64 -w0)
    proxy: tor                    # Previous proxy (could be omitted to connect with clear IP)
    hostkeys:                     # SSH Server public key (ssh-keyscan -H -p <port> <host>)
      - "One per line"
ROUTES:                           # List of routes
  default:                        # Route names
    proxy: tor                    # Proxy for this route
    network: default              # Network (10.0.0.0/8 or default)
DNS:                              # List of custom DNS entries
  - name: dashboard.dockeranon    # DNS entry name
    type: A                       # DNS entry type (A, AAAA, CNAME, MX, NS)
    value: 192.168.5.254          # DNS entry value
```


## Usage
Launch dockeranon.py. Commands can be listed with 'help' and any command can be detailed with '<command> help'
### Commands
 * **set**: override a value from 'config.yaml'
 * **showconfig**: display the current configuration
 * **launch**: build and launch dockers
 * **status**: check if containers are running (and check IP)
 * **connect**: launch VNC client and display noVNC url
 * **savegateway**: save current gateway configuration at gateway.yaml
 * **exit**: exit dockeranon and DELETE containers
### Workstation
Once connected to workstation, you can use it without any other configuration.

Share directory is available in /home/user/Share.

You can access to gateway configuration panel using 'http://dashboard.dockernanon' or 'http://192.168.5.254'. Domain work only in workstation, IP work on workstation and host.


## OPSEC
When using status command, two requests are made:
 * one to *https://api.ipify.org* on Gateway
 * one to *https://icanhazip.com* on Workstation