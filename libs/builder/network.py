import docker

client = docker.from_env()


class NetworkBuilder:
    NETWORK = None
    _DEFAULT_NETWORK = None

    def __init__(self, name='dockeranon_net', range='192.168.5.0/24', gw='192.168.5.254'):
        self.network = NetworkBuilder.NETWORK
        if self.network is not None:
            return
        # Check if network exists
        for net in client.networks.list():
            if net.attrs.get('Name') == name:
                NetworkBuilder.NETWORK = client.networks.get(net.id)
            elif net.attrs.get('Name') == 'bridge':
                NetworkBuilder._DEFAULT_NETWORK = client.networks.get(net.id)
        if NetworkBuilder.NETWORK is None:
            # Create if not exists
            ipam_pool = docker.types.IPAMPool(
                subnet=range
            )
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[ipam_pool]
            )
            NetworkBuilder.NETWORK = client.networks.create(
                name,
                driver="bridge",
                ipam=ipam_config
            )
        self.network = NetworkBuilder.NETWORK

    def connect(self, container_builder, ip):
        self.network.connect(container_builder.container,
                             ipv4_address=ip)
        self._DEFAULT_NETWORK.disconnect(container_builder.container)

    @property
    def gateway(self):
        if self.network is None:
            return None
        return self.network.attrs.get('IPAM').get('Config')[0].get('Gateway')

    @property
    def range(self):
        if self.network is None:
            return None
        return self.network.attrs.get('IPAM').get('Config')[0].get('Subnet')

    @property
    def name(self):
        if self.network is None:
            return None
        return self.network.attrs.get('Name')

    @staticmethod
    def clean():
        if NetworkBuilder.NETWORK is not None:
            NetworkBuilder.NETWORK.remove()
