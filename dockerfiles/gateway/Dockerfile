FROM python:3.8-alpine as builder
# Création du venv
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH" VIRTUAL_ENV="/venv"
# Install
RUN python3 -m pip install --no-cache-dir pproxy bottle pyyaml dnslib



FROM python:3.8-alpine
ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GATEWAY_IP=<GATEWAY_IP>
# Install base packages
RUN apk add --no-cache git tor iptables iproute2 curl netcat-openbsd openssh sshpass
# Activate venv
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH" VIRTUAL_ENV="/venv"
# Copy files
COPY torrc /etc/tor/torrc
COPY torrc /etc/tor/torrc.default
COPY entrypoint.sh /bin/entrypoint.sh
RUN chown root: /bin/entrypoint.sh && chmod 700 /bin/entrypoint.sh
COPY webui/ /root/webui/
COPY gateway.yaml /root/webui/gateway.yaml
RUN chown root: /root/webui/webui.py && chmod 700 /root/webui/webui.py
# Launch entrypoint
WORKDIR /root/webui
CMD /bin/entrypoint.sh
