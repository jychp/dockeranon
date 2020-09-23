import socketserver
import multiprocessing

import yaml
from dnslib import *


class UDPRequestHandler(socketserver.BaseRequestHandler):
    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)

    def handle(self):
        try:
            data = self.get_data()
            self.send_data(self.dns_response(data))
        except Exception:
            pass

    @staticmethod
    def dns_response(data):
        request = DNSRecord.parse(data)
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        qname = request.q.qname
        qn = str(qname)
        qtype = request.q.qtype
        qt = QTYPE[qtype]
        entries = DNSServer.get_dom(qn)
        if entries is None:
            if qn[-1] == '.':
                dom = qn[0:-1]
            else:
                dom = qn
            q = DNSRecord(q=DNSQuestion(dom, qtype))
            dns_host, dns_port = DNSServer.get_forwarder()
            a_pkt = q.send(dns_host, dns_port, tcp=False)
            a = DNSRecord.parse(a_pkt)
            for r in a.rr:
                reply.add_answer(r)
            return reply.pack()
        for q, rdata_list in entries.items():
            if qt != '*' and qtype != q:
                continue
            for rdata in rdata_list:
                rqt = rdata.__class__.__name__
                reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, rqt), rclass=1, ttl=60, rdata=rdata))
        return reply.pack()


class DNSServer(socketserver.UDPServer, multiprocessing.Process):
    _ZONE = {}
    _FORWARDER_HOST = '127.0.0.1'
    _FORWARDER_PORT = 53
    _COMMON_LOCK = multiprocessing.Lock()

    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self)
        self.name = 'dnsserver'
        self.host = args[0]
        socketserver.UDPServer.__init__(self, *args, **kwargs)
        self.update_zone_lock = multiprocessing.Lock()
        self.zone_file = 'gateway.yaml'

    def ask_for_reload(self):
        self.update_zone_lock.acquire()

    def run(self):
        while True:
            self.handle_request()
            # Check for update
            test = self.update_zone_lock.acquire(block=False)
            if test:
                self.update_zone_lock.release()
            else:
                self.load_zone()
                self.update_zone_lock.release()

    @staticmethod
    def set_forwarder(host, port=53):
        DNSServer._FORWARDER_HOST = host
        DNSServer._FORWARDER_PORT = port

    @staticmethod
    def get_forwarder():
        return DNSServer._FORWARDER_HOST, DNSServer._FORWARDER_PORT

    def load_zone(self):
        with open(self.zone_file) as fd:
            data = yaml.load(fd, Loader=yaml.FullLoader)
            DNSServer._ZONE = {}
            for e in data.get('DNS'):
                domain = e.get('name')
                rqt = e.get('type')
                value = e.get('value')
                if domain[-1] != '.':
                    domain += '.'
                if domain not in DNSServer._ZONE:
                    DNSServer._ZONE[domain] = {}
                qtype = getattr(QTYPE, rqt)
                if qtype not in DNSServer._ZONE[domain]:
                    DNSServer._ZONE[domain][qtype] = []
                if rqt == 'A':
                    func = A
                elif rqt == 'NS':
                    func = NS
                elif rqt == 'CNAME':
                    func = CNAME
                elif rqt == 'MX':
                    func = MX
                elif rqt == 'AAAA':
                    func = AAAA
                else:
                    func = None
                if func is not None:
                    DNSServer._ZONE[domain][qtype].append(func(value))

    @staticmethod
    def get_dom(qn):
        return DNSServer._ZONE.get(qn)

    def dummy_request(self):
        try:
            q = DNSRecord(q=DNSQuestion('localhost', 1))
            q.send(self.host[0], self.host[1], tcp=False, timeout=1)
        except socket.timeout:
            pass
