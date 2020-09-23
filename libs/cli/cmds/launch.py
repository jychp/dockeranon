import time

from libs.cli.printer import Printer
from libs.builder.network import NetworkBuilder
from libs.builder.gateway import GatewayBuilder
from libs.builder.workstation import WorkstationBuilder
from libs.cli.config import Config
from libs.errors import BuilderError


class CMDLaunch:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info("launch the containers with the current configuration")
            Printer.info("usage:")
            Printer.info("  launch")
            Printer.newline()
            return True
        elif cmd == '':
            Printer.newline()
            try:
                # Build & Launch
                Printer.info('Creating network ...')
                network = NetworkBuilder(name=Config.get('NETWORK_NAME'),
                                         range=Config.get('NETWORK_RANGE'))
                Printer.info('Building gateway image ...')
                gateway = GatewayBuilder(name=Config.get('GATEWAY_NAME'),
                                         net=Config.get('NETWORK_RANGE'),
                                         ip=Config.get('GATEWAY_IP'))
                Printer.info('Building workstation image ...')
                workstation = WorkstationBuilder(name=Config.get('WORKSTATION_NAME'),
                                                 apps=Config.get('WORKSTATION_APPS'),
                                                 ip=Config.get('WORKSTATION_IP'))
                Printer.info('Connecting containers to network ...')
                network.connect(gateway, ip=Config.get('GATEWAY_IP'))
                network.connect(workstation, ip=Config.get('WORKSTATION_IP'))
                time.sleep(5)
                if not workstation.change_gateway():
                    Printer.error('Can not change gateway of workstation')
                    return False
                if Config.get('MOUNT_POINT_USE'):
                    Printer.success('Containers launched, share directory: /home/user/Share => {0}'.format(Config.get('MOUNT_POINT')))
                else:
                    Printer.success('Containers launched')
                Printer.warning("OPSEC: check IPs with 'status' before using Workstation.")
            except BuilderError as e:
                Printer.error(e)
            Printer.newline()
        else:
            Printer.error("Bad arguments. Use 'launch help' for more information.")
            return False

    @staticmethod
    def help():
        return 'build and launch dockers'
