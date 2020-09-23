FROM <WORKSTATION_IMAGE>
USER root
RUN apt-get update && apt-get install -y curl net-tools jq openssl git python3-pip
<WORKSTATION_APPS>
USER user
RUN mkdir /home/user/Share