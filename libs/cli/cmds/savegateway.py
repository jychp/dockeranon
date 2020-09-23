from libs.cli.printer import Printer
from libs.builder.gateway import GatewayBuilder
from libs.cli.config import Config


class CMDSaveGateway:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info("save current gateway configuration at gateway.yaml")
            Printer.info("usage:")
            Printer.info("  savegateway")
            Printer.newline()
            return True
        elif cmd == '':
            Printer.newline()
            try:
                GatewayBuilder.save()
                Printer.success('Gateway proxies, routes and dns saved')
            except Exception as e:
                Printer.error(str(e))
                Printer.error("Error while connecting to gateway")
            Printer.newline()
        else:
            Printer.error("Bad arguments. Use 'launch help' for more information.")
            return False

    @staticmethod
    def help():
        return 'save current gateway configuration at gateway.yaml'
