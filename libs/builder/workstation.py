import os
import shutil
from tempfile import TemporaryDirectory

import docker
from docker.types import Mount

from libs.cli.config import Config

client = docker.from_env()


class WorkstationBuilder:
    CONTAINER_ID = None

    def __init__(self, name='dockeranon_workstation', apps='', ip='192.168.5.1'):
        if WorkstationBuilder.CONTAINER_ID is not None:
            return
        with TemporaryDirectory() as dir_name:
            # Copy files
            for f in os.listdir('dockerfiles/workstation'):
                if f == 'Dockerfile':
                    with open('dockerfiles/workstation/Dockerfile') as fd_in:
                        with open('{0}/Dockerfile'.format(dir_name), 'w') as fd_out:
                            for line in fd_in.readlines():
                                line = line.replace('<WORKSTATION_IMAGE>', Config.get('WORKSTATION_IMAGE'))
                                line = line.replace('<WORKSTATION_APPS>', self._apps_install(apps))
                                fd_out.write(line)
                else:
                    shutil.copy('dockerfiles/workstation/{0}'.format(f), dir_name)

            # Build image
            client.images.build(pull=True,
                                path=dir_name,
                                tag=name)

            # Launch
            mounts = []
            if Config.get('MOUNT_POINT_USE'):
                try:
                    os.makedirs(Config.get('MOUNT_POINT'))
                except FileExistsError:
                    pass
                mount = Mount(target='/home/user/Share',
                              source=Config.get('MOUNT_POINT'),
                              type='bind')
                mounts.append(mount)
            container = client.containers.run(name,
                                              cap_add=["NET_ADMIN"],
                                              detach=True,
                                              hostname=Config.get('WORKSTATION_HOSTNAME'),
                                              mounts=mounts)
            WorkstationBuilder.CONTAINER_ID = container.id

    @property
    def container(self):
        return WorkstationBuilder.get_container()

    def _apps_install(self, apps):
        apps = apps.split(',')
        if len(apps) > 0:
            return 'RUN apt-get update && apt-get install -y {0}'.format(' '.join(apps))
        return ''

    def change_gateway(self):
        code, _ = self.container.exec_run('ip route del default', user='root')
        if code != 0:
            return False
        code, _ = self.container.exec_run('ip route add default via {0}'.format(Config.get('GATEWAY_IP')), user='root')
        if code != 0:
            return False
        return True

    @staticmethod
    def get_container():
        if WorkstationBuilder.CONTAINER_ID is None:
            return None
        return client.containers.get(WorkstationBuilder.CONTAINER_ID)

    @staticmethod
    def clean():
        container = WorkstationBuilder.get_container()
        if container is not None:
            container.stop()
            container.remove()
