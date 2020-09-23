import yaml


class Data:
    _PROXIES = {}
    _ROUTES = {}
    _DNS = {}

    @staticmethod
    def load(filename='gateway.yaml'):
        with open(filename) as fd:
            data = yaml.load(fd, Loader=yaml.FullLoader)
            Data._PROXIES = data.get('PROXIES', {})
            Data._ROUTES = data.get('ROUTES', {})
            Data._DNS = data.get('DNS', {})

    @staticmethod
    def get(name):
        if name == 'proxies':
            return Data._PROXIES
        elif name == 'routes':
            return Data._ROUTES
        elif name == 'dns':
            return Data._DNS

    @staticmethod
    def set(name, values):
        if name == 'proxies':
            Data._PROXIES = values
        elif name == 'routes':
            Data._ROUTES = values
        elif name == 'dns':
            Data._DNS = values

    @staticmethod
    def save(filename='gateway.yaml'):
        with open(filename, 'w') as fd:
            data = {'PROXIES': Data._PROXIES,
                    'ROUTES': Data._ROUTES,
                    'DNS': Data._DNS}
            yaml.dump(data, fd)
