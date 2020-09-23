import yaml


class Config:
    KEEP_RUNNING = True
    _OPTIONS = None

    @staticmethod
    def _load():
        if Config._OPTIONS is not None:
            return
        try:
            with open('config.yaml') as fc:
                Config._OPTIONS = yaml.load(fc, Loader=yaml.FullLoader)
        except FileNotFoundError:
            Config._OPTIONS = {'NETWORK_NAME': 'dockeranon_net',
                               'NETWORK_RANGE': '192.168.5.0/24',
                               'GATEWAY_NAME': 'dockeranon_gateway',
                               'GATEWAY_IP': '192.168.5.254',
                               'WORKSTATION_IMAGE': 'jychp/xubuntu:latest',
                               'WORKSTATION_NAME': 'dockeranon_workstation',
                               'WORKSTATION_IP': '192.168.5.10',
                               'WORKSTATION_RESOLUTION': '1600x1024',
                               'WORKSTATION_PASSWD': 'password',
                               'WORKSTATION_APPS': '',
                               'WORKSTATION_HOSTNAME': 'ubuntu',
                               'VNC_CLIENT': '/usr/bin/vncviewer',
                               'MOUNT_POINT': '/dev/shm/dockeranon',
                               'MOUNT_POINT_USE': True
                               }

    @staticmethod
    def set(key, value):
        Config._load()
        if value.lower() == 'true':
            Config._OPTIONS[key] = True
        elif value.lower() == 'false':
            Config._OPTIONS[key] = False
        else:
            Config._OPTIONS[key] = value

    @staticmethod
    def get(key):
        Config._load()
        return Config._OPTIONS.get(key)

    @staticmethod
    def get_all():
        Config._load()
        return Config._OPTIONS.items()
