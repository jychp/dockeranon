import os
from urllib.parse import urlencode

import bottle

from models.data import Data
from models.proxy import Proxy
from models.dns import DNSServer, UDPRequestHandler


Data.load()
DNS_HOST = os.getenv('GATEWAY_IP')
DNS_FORWARDER = '127.0.0.1'
DNS_FORWARDER_PORT = 5353
DNS = DNSServer((DNS_HOST, 53), UDPRequestHandler)
# Launch DNS
DNS.load_zone()
DNS.set_forwarder(DNS_FORWARDER, 5353)
DNS.start()
# Launch Proxy
Proxy.reset()
Proxy.build_all(Data.get('proxies'))
Proxy.prepare(Data.get('routes'))
Proxy.exec()


@bottle.route('/static/<filename:path>')
def server_static(filename):
    return bottle.static_file(filename, root='static')


@bottle.route('/save')
def download():
    return bottle.static_file('gateway.yaml', root='/root/webui', download='gateway.yaml')


@bottle.route('/')
def index():
    return bottle.redirect('/proxy')


@bottle.route("/proxy")
@bottle.view('views/proxy.html')
def proxy():
    proxy_list = []
    for p_name, p_data in Data.get('proxies').items():
        proxy_list.append({"name": p_name,
                           "type": p_data.get('type'),
                           "host": "{0}:{1}".format(p_data.get('host', '127.0.0.1'), p_data.get('port', 9050)),
                           "proxy": p_data.get("proxy", "-")})
    return {"title": "DockerAnon | Proxy",
            "proxy": proxy_list,
            "msg": bottle.request.query.msg}


@bottle.route("/routes")
@bottle.view('views/routes.html')
def routes():
    route_list = []
    for r_name, r_data in Data.get('routes').items():
        route_list.append({"name": r_name,
                           "network": r_data.get("network"),
                           "proxy": r_data.get("proxy")})
    return {"title": "DockerAnon | Routes",
            "route": route_list,
            "msg": bottle.request.query.msg}


@bottle.route("/dns")
@bottle.view('views/dns.html')
def dns():
    dns_list = []
    i = 0
    for d in Data.get('dns'):
        entry = d.copy()
        entry['id'] = 0
        dns_list.append(entry)
        i += 1
    return {"title": "DockerAnon | DNS",
            "dns": dns_list,
            "msg": bottle.request.query.msg}


@bottle.route("/proxy/delete/<proxy_name>")
def proxy_delete(proxy_name):
    new_proxies = Data.get('proxies').copy()
    new_proxies.pop(proxy_name)
    # Rebuild chains
    Proxy.reset()
    Proxy.build_all(new_proxies)
    try:
        Proxy.prepare(Data.get('routes'))
        Data.set('proxies', new_proxies)
        Data.save()
        Proxy.exec()
        return bottle.redirect('/proxy')
    except Exception as e:
        return bottle.redirect('/proxy?{0}'.format(urlencode({'msg': str(e)})))


@bottle.route("/dns/delete/<dns_id:int>")
def dns_delete(dns_id):
    new_dns = Data.get('dns')[:]
    new_dns.pop(dns_id)
    Data.set('dns', new_dns)
    Data.save()
    DNS.ask_for_reload()
    return bottle.redirect('/dns')


@bottle.route("/routes/delete/<route_name>")
def routes_delete(route_name):
    new_routes = Data.get('routes').copy()
    new_routes.pop(route_name)
    # Rebuild chains
    Proxy.reset()
    Proxy.build_all(Data.get('proxies'))
    try:
        Proxy.prepare(new_routes)
        Data.set('routes', new_routes)
        Data.save()
        Proxy.exec()
        return bottle.redirect('/routes')
    except Exception as e:
        return bottle.redirect('/routes?{0}'.format(urlencode({'msg': str(e)})))


@bottle.route("/proxy/restart")
def proxy_restart():
    # Rebuild chains
    Proxy.reset()
    Proxy.build_all(Data.get('proxies'))
    try:
        Proxy.prepare(Data.get('routes'))
        Proxy.exec()
        return bottle.redirect('/proxy')
    except Exception as e:
        return bottle.redirect('/proxy?{0}'.format(urlencode({'msg': str(e)})))


@bottle.route("/routes/restart")
def routes_restart():
    # Rebuild chains
    Proxy.reset()
    Proxy.build_all(Data.get('proxies'))
    try:
        Proxy.prepare(Data.get('routes'))
        Proxy.exec()
        return bottle.redirect('/routes')
    except Exception as e:
        return bottle.redirect('/routes?{0}'.format(urlencode({'msg': str(e)})))


@bottle.route("/dns/restart")
def dns_restart():
    # Relaunch DNS Server
    DNS.ask_for_reload()
    return bottle.redirect('/dns')


@bottle.route("/proxy/add", method=('POST', 'GET'))
@bottle.view('views/proxy_add.html')
def proxy_add():
    if bottle.request.forms.get('name') is not None:
        proxy = {}
        proxy['type'] = bottle.request.forms.get('ptype')
        if proxy['type'] is None:
            return bottle.redirect('/proxy/add?{0}'.format(urlencode({'msg': 'Type field is mandatory'})))
        proxy['host'] = bottle.request.forms.get('host')
        if proxy['host'] is None:
            return bottle.redirect('/proxy/add?{0}'.format(urlencode({'msg': 'Host field is mandatory'})))
        proxy['port'] = bottle.request.forms.get('port')
        if proxy['host'] is None:
            return bottle.redirect('/proxy/add?{0}'.format(urlencode({'msg': 'Port field is mandatory'})))
        user = bottle.request.forms.get('user')
        if user is None and proxy['type'] == 'ssh':
            return bottle.redirect('/proxy/add?{0}'.format(urlencode({'msg': 'User field is mandatory for SSH'})))
        elif user is not None:
            proxy['user'] = user
        password = bottle.request.forms.get('password')
        if password is not None:
            proxy['password'] = password
        sshkey = bottle.request.forms.get('sshkey')
        if sshkey is not None:
            proxy['sshkey'] = sshkey
        if proxy['type'] == 'ssh' and password is None and sshkey is None:
            return bottle.redirect('/proxy/add?{0}'.format(urlencode({'msg': 'You must provide password or SSH key for SSH'})))
        previous = bottle.request.forms.get('previous')
        if previous != 'None':
            proxy['proxy'] = previous
        hostkeys = bottle.request.forms.get('hostkeys')
        if len(hostkeys) > 0:
            proxy['hostkeys'] = hostkeys.split('\n')
        new_proxies = Data.get('proxies').copy()
        new_proxies[bottle.request.forms.get('name')] = proxy
        # Rebuild chains
        Proxy.reset()
        Proxy.build_all(new_proxies)
        try:
            Proxy.prepare(Data.get('routes'))
            Data.set('proxies', new_proxies)
            Data.save()
            Proxy.exec()
            return bottle.redirect('/proxy')
        except Exception as e:
            return bottle.redirect('/proxy?{0}'.format(urlencode({'msg': str(e)})))

    return {"title": "DockerAnon | Proxy",
            "proxy": list(Data.get('proxies').keys()),
            "msg": bottle.request.query.msg}


@bottle.route("/routes/add", method=('POST', 'GET'))
@bottle.view('views/routes_add.html')
def routes_add():
    if bottle.request.forms.get('name') is not None:
        route = {}
        route['network'] = bottle.request.forms.get('network')
        if route['network'] is None:
            return bottle.redirect('/routes/add?{0}'.format(urlencode({'msg': 'Network field is mandatory'})))
        route['proxy'] = bottle.request.forms.get('proxy')
        new_routes = Data.get('routes').copy()
        new_routes[bottle.request.forms.get('name')] = route
        # Rebuild chains
        Proxy.reset()
        Proxy.build_all(Data.get('proxies'))
        try:
            Proxy.prepare(new_routes)
            Data.set('routes', new_routes)
            Data.save()
            Proxy.exec()
            return bottle.redirect('/routes')
        except Exception as e:
            return bottle.redirect('/routes?{0}'.format(urlencode({'msg': str(e)})))

    return {"title": "DockerAnon | Routes",
            "proxy": list(Data.get('proxies').keys()),
            "msg": bottle.request.query.msg}


@bottle.route("/dns/add", method=('POST', 'GET'))
@bottle.view('views/dns_add.html')
def routes_add():
    if bottle.request.forms.get('name') is not None:
        dns_entry = {}
        dns_entry['name'] = bottle.request.forms.get('name')
        dns_entry['type'] = bottle.request.forms.get('dtype')
        dns_entry['value'] = bottle.request.forms.get('value')
        if dns_entry['value'] is None or dns_entry['value'] == '':
            return bottle.redirect('/dns/add?{0}'.format(urlencode({'msg': 'Value field is mandatory'})))
        new_dns = Data.get('dns')[:]
        new_dns.append(dns_entry)
        Data.set('dns', new_dns)
        Data.save()
        DNS.ask_for_reload()
        return bottle.redirect('/dns')

    return {"title": "DockerAnon | DNS",
            "msg": bottle.request.query.msg}


bottle.run(bottle.app(), host='0.0.0.0', port=80, debug=False, reloader=False)
