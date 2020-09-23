import docker

from libs.cli.printer import Printer
from libs.cli.config import Config
from libs.builder import WorkstationBuilder, GatewayBuilder, NetworkBuilder

client = docker.from_env()


class CMDExit:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info("exit dockeranon and DELETE containers")
            Printer.info("usage:")
            Printer.info("  exit")
            Printer.newline()
            return True
        else:
            Config.KEEP_RUNNING = False
            # Delete containers
            Printer.newline()
            Printer.info('Delete Workstation ...')
            WorkstationBuilder.clean()
            Printer.info('Delete Gateway ...')
            GatewayBuilder.clean()
            # Delete network
            NetworkBuilder.clean()
            Printer.newline()
            return True

    @staticmethod
    def help():
        return 'exit dockeranon and DELETE containers'
