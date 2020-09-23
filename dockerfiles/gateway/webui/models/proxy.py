import os
import base64
import shutil
import time
import stat


class Proxy:
    _PRIVATEKEYS = []
    _HOSTKEYS = []
    _PROXIES = {}
    _REDIRECT = {}
    _USE_TOR = False
    _TOR_PROXY = None
    _NEXT_PORT = 7000
    _CMDS = []
    _IPTABLES = []

    def __init__(self, proxy_name, proxy_data):
        # Data
        self.name = proxy_name
        self.proxy_type = proxy_data.get('type').lower()
        if self.proxy_type == 'tor':
            if Proxy._USE_TOR:
                raise Exception('You can not use only one Tor instance')
            else:
                Proxy._USE_TOR = True
        self.host = proxy_data.get('host')
        self.port = proxy_data.get('port')
        self.user = proxy_data.get('user')
        self.password = proxy_data.get('password')
        if proxy_data.get('key') is not None:
            self.ssh_key = base64.b64decode(proxy_data.get('key'))
        else:
            self.ssh_key = None
        self.previous_proxy_name = proxy_data.get('proxy')
        for h in proxy_data.get('hostkeys', []):
            Proxy._HOSTKEYS.append(h)
        # Register
        Proxy._PROXIES[self.name] = self
        # Internal
        self._pproxy_chain = None
        self._intermediate_socks5 = None

    @property
    def previous_proxy(self):
        if self.previous_proxy_name in Proxy._PROXIES:
            return Proxy._PROXIES[self.previous_proxy_name]
        return None

    @staticmethod
    def build_all(proxies):
        for proxy_name, proxy_data in proxies.items():
            Proxy(proxy_name, proxy_data)

    def create_redirect(self):
        redirect_port = Proxy._NEXT_PORT
        Proxy._NEXT_PORT += 1
        cmd = 'pproxy -l redir://0.0.0.0:{0} -r {1}'.format(redirect_port, self.get_pproxy_chain())
        Proxy._CMDS.append(cmd)
        Proxy._REDIRECT[self.name] = redirect_port

    def get_intermediate_socks5(self):
        # Existing
        if self._intermediate_socks5:
            return '127.0.0.1', self._intermediate_socks5
        # Create
        if self.proxy_type == 'tor':
            return '127.0.0.1', 9050
        elif self.proxy_type == 'ssh':
            self._intermediate_socks5 = self._launch_ssh()
            return '127.0.0.1', self._intermediate_socks5
        else:
            # Launch intermediate proxy
            cmd = 'pproxy -l socks5://127.0.0.1:{0} -r {1}'.format(Proxy._NEXT_PORT, self.get_pproxy_chain())
            self._intermediate_socks5 = Proxy._NEXT_PORT
            Proxy._NEXT_PORT += 1
            Proxy._CMDS.append(cmd)
            return '127.0.0.1', self._intermediate_socks5

    def get_pproxy_chain(self):
        if self._pproxy_chain is not None:
            return self._pproxy_chain
        # Launch
        if self.proxy_type == 'tor':
            if self.previous_proxy_name is not None:
                Proxy._TOR_PROXY = self.previous_proxy.get_intermediate_socks5()
            self._pproxy_chain = 'socks5://127.0.0.1:9050'
            return self._pproxy_chain
        elif self.proxy_type in ('socks5', 'socks4', 'http', 'httponly', 'ss', 'ssr'):
            if self.user is not None and self.password is not None:
                server = '{0}://{1}:{2}@{3}:{4}'.format(self.proxy_type,
                                                        self.user,
                                                        self.password,
                                                        self.host,
                                                        self.port)
            else:
                server = '{0}://{1}:{2}'.format(self.proxy_type,
                                                self.host,
                                                self.port)
            # Add previous
            if self.previous_proxy_name is not None:
                self._pproxy_chain = self.previous_proxy.get_pproxy_chain() + '__' + server
            else:
                self._pproxy_chain = server
            return self._pproxy_chain
        elif self.proxy_type == 'ssh':
            ip, port = self.get_intermediate_socks5()
            self._pproxy_chain = 'socks5://{0}:{1}'.format(ip, port)
            return self._pproxy_chain
        else:
            raise Exception("Unknown proxy type '{0}'".format(self.proxy_type))

    def _launch_ssh(self):
        if self.proxy_type != 'ssh':
            return
        ssh_cmd = ''
        # Manage previous proxy
        if self.previous_proxy_name is not None:
            previous_ip, previous_port = self.previous_proxy.get_intermediate_socks5()
            ssh_proxy = "-o 'ProxyCommand nc -x {0}:{1} %h %p'".format(previous_ip,
                                                                       previous_port)
        else:
            ssh_proxy = ''
        # Use sshpass if needed
        if self.password is not None:
            ssh_cmd = 'sshpass -p {0} '.format(self.password)
        # Build cmd
        socks_port = Proxy._NEXT_PORT
        Proxy._NEXT_PORT += 1
        ssh_cmd += 'ssh -v -N -T -D {0} {1} '.format(socks_port, ssh_proxy)
        # Use key if needed
        if self.ssh_key is not None:
            ssh_cmd += '-i /tmp/sshkey_{0} '.format(len(Proxy._PRIVATEKEYS))
            Proxy._PRIVATEKEYS.append(self.ssh_key)
        # Build cmd
        ssh_cmd += '{0}@{1} -p {2}'.format(self.user, self.host, self.port)
        Proxy._CMDS.append(ssh_cmd)
        return socks_port

    @staticmethod
    def reset():
        Proxy._PRIVATEKEYS = []
        Proxy._HOSTKEYS = []
        Proxy._PROXIES = {}
        Proxy._REDIRECT = {}
        Proxy._USE_TOR = False
        Proxy._TOR_PROXY = None
        Proxy._NEXT_PORT = 7000
        Proxy._CMDS = []
        Proxy._IPTABLES = []

    @staticmethod
    def prepare(routes):
        # Launch proxies
        for route_name, route_data in routes.items():
            if route_data.get('proxy') not in Proxy._PROXIES:
                raise Exception('Proxy {0} is missing'.format(route_data.get('proxy')))
            if route_data.get('proxy') in Proxy._REDIRECT:
                continue
            # Create redirect
            Proxy._PROXIES[route_data.get('proxy')].create_redirect()
        # Prepare IPTables
        default_rule = None
        for route_name, route_data in routes.items():
            if route_data.get('network') == 'default':
                default_rule = 'iptables -t nat -A GATEWAY -p tcp -j REDIRECT --to-ports {0}'.format(Proxy._REDIRECT[route_data.get('proxy')])
            else:
                ipt_cmd = 'iptables -t nat -A GATEWAY -d {1} -p tcp -j REDIRECT --to-ports {0}'.format(Proxy._REDIRECT[route_data.get('proxy')],
                                                                                                       route_data.get('network'))
                Proxy._IPTABLES.append(ipt_cmd)
        if default_rule is not None:
            Proxy._IPTABLES.append(default_rule)

    @staticmethod
    def exec():
        # Clean old
        os.system('killall pproxy')
        os.system('killall tor')
        os.system('killall ssh')
        time.sleep(5)
        # Restore torrc
        shutil.copy('/etc/tor/torrc.default', '/etc/tor/torrc')
        if Proxy._TOR_PROXY is not None:
            with open('/etc/tor/torrc', 'a') as fd:
                fd.write('\nSocks5Proxy {0}:{1}\n'.format(Proxy._TOR_PROXY[0], Proxy._TOR_PROXY[1]))
        # Relaunch Tor
        os.system('/usr/bin/tor -f /etc/tor/torrc')
        time.sleep(5)
        with open('/etc/resolv.conf', 'w') as fd:
            fd.write('nameserver {0}'.format(os.getenv('GATEWAY_IP')))
        # Write private keys
        i = 0
        for pk in Proxy._PRIVATEKEYS:
            with open('/tmp/sshkey_{0}'.format(i), 'w') as fd:
                fd.write(pk.decode('utf-8'))
            os.chmod('/tmp/sshkey_{0}'.format(i), stat.S_IRUSR)
            i += 1
        # Write known hosts
        with open('/root/.ssh/known_hosts', 'w') as fd:
            for h in Proxy._HOSTKEYS:
                fd.write('{0}\n'.format(h))
        # Launch cmd
        for cmd in Proxy._CMDS:
            os.system(cmd + ' &')
        # Apply iptables
        os.system('iptables -F')
        os.system('iptables -t nat -F')
        os.system('iptables -t nat -N GATEWAY')
        os.system('iptables -A OUTPUT -m conntrack --ctstate INVALID -j DROP')
        os.system('iptables -A OUTPUT -m state --state INVALID -j DROP')
        os.system('iptables -A OUTPUT ! -o lo ! -d 127.0.0.1 ! -s 127.0.0.1 -p tcp -m tcp --tcp-flags ACK,FIN ACK,FIN -j DROP')
        os.system('iptables -A OUTPUT ! -o lo ! -d 127.0.0.1 ! -s 127.0.0.1 -p tcp -m tcp --tcp-flags ACK,RST ACK,RST -j DROP')
        os.system('iptables -t nat -A GATEWAY -p tcp -d 127.0.0.0/8 -j RETURN')
        os.system('iptables -t nat -A GATEWAY -p udp -d 127.0.0.0/8 -j RETURN')
        os.system('iptables -t nat -A GATEWAY -p tcp -d {0} -j RETURN'.format(os.getenv('GATEWAY_IP')))
        os.system('iptables -t nat -A GATEWAY -p udp -d {0} -j RETURN'.format(os.getenv('GATEWAY_IP')))
        os.system('iptables -t nat -A GATEWAY -p udp --dport 53 -j REDIRECT --to-ports 53')
        os.system('iptables -t nat -A GATEWAY -p udp -j REDIRECT --to-port 4073')
        for ipt in Proxy._IPTABLES:
            os.system(ipt)
        os.system('iptables -t nat -A PREROUTING -i eth1 -j GATEWAY')
