import os
import shutil
from tempfile import TemporaryDirectory
import requests

import docker
import yaml

from libs.cli.config import Config

client = docker.from_env()


class GatewayBuilder:
    CONTAINER = None
    CONTAINER_ID = None

    def __init__(self, name='dockeranon_gateway', net='192.168.5.0/24', ip='192.168.5.254'):
        if GatewayBuilder.CONTAINER_ID is not None:
            return

        with TemporaryDirectory() as dir_name:
            # Copy files
            for f in os.listdir('dockerfiles/gateway'):
                file_name = 'dockerfiles/gateway/{0}'.format(f)
                if os.path.isdir(file_name):
                    shutil.copytree(file_name, '{0}/{1}'.format(dir_name, f))
                else:
                    if f == 'Dockerfile':
                        with open('dockerfiles/gateway/Dockerfile') as fd_in:
                            with open('{0}/Dockerfile'.format(dir_name), 'w') as fd_out:
                                for line in fd_in.readlines():
                                    line = line.replace('<GATEWAY_IP>', ip)
                                    fd_out.write(line)
                    else:
                        shutil.copy('dockerfiles/gateway/{0}'.format(f), dir_name)
            # Copy gateway conf
            shutil.copy('gateway.yaml', dir_name)
            # Build image
            client.images.build(pull=True,
                                path=dir_name,
                                tag=name)
            # Launch
            container = client.containers.run(name,
                                              cap_add=["NET_ADMIN"],
                                              hostname=Config.get('GATEWAY_HOSTNAME'),
                                              detach=True)
            GatewayBuilder.CONTAINER_ID = container.id

    @property
    def container(self):
        return GatewayBuilder.get_container()

    @staticmethod
    def clean():
        container = GatewayBuilder.get_container()
        if container is not None:
            container.stop()
            container.remove()

    @staticmethod
    def get_container():
        if GatewayBuilder.CONTAINER_ID is None:
            return None
        return client.containers.get(GatewayBuilder.CONTAINER_ID)

    @staticmethod
    def save(output_file='gateway.yaml'):
        req = requests.get('http://{0}/save'.format(Config.get('GATEWAY_IP')), timeout=30)
        if req.status_code != 200:
            raise Exception('HTTP Error {0}'.format(req.status_code))
        with open(output_file, 'wb') as fd:
            fd.write(req.content)
        return True
