import docker

from libs.cli.printer import Printer
from libs.builder import WorkstationBuilder, GatewayBuilder

client = docker.from_env()


class CMDStatus:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info("display containers status and ip")
            Printer.info("usage:")
            Printer.info("  exit")
            Printer.newline()
            return True
        else:
            Printer.newline()
            # Check if running
            if WorkstationBuilder.get_container() is None:
                Printer.warning('Worksation status: OFF')
                Printer.newline()
                return False
            else:
                if WorkstationBuilder.get_container().status != 'running':
                    Printer.warning('Worksation status: OFF')
                    Printer.newline()
                    return False
                Printer.info('Worksation status: ON')
            if GatewayBuilder.get_container() is None:
                Printer.warning('Gateway status: OFF')
                Printer.newline()
                return False
            else:
                if GatewayBuilder.get_container().status != 'running':
                    Printer.warning('Gateway status: OFF')
                    Printer.newline()
                    return False
                Printer.info('Gateway status: ON')
            # Check IPs
            req = GatewayBuilder.get_container().exec_run('curl --silent https://api.ipify.org', user='root')
            real_ip = req.output.decode().strip()
            if real_ip == '':
                Printer.error('Gateway not connected to internet')
                Printer.newline()
                return False
            else:
                Printer.info('Clear IP: {0}'.format(real_ip))
            req = WorkstationBuilder.get_container().exec_run('curl --silent https://icanhazip.com/', user='root')
            tor_ip = req.output.decode().strip()
            if tor_ip == '':
                Printer.error('Workstation can not connect to internet')
                Printer.newline()
                return False
            else:
                Printer.info('Workstation default IP: {0}'.format(tor_ip))
            if tor_ip == real_ip:
                Printer.error('YOU DEFAULT ROUTE LEAK YOUR IP !')
                Printer.newline()
                return False
            else:
                Printer.success('DockerAnon is running, you can connect to the Workstation.')
            Printer.newline()

    @staticmethod
    def help():
        return 'display containers status and ip'
