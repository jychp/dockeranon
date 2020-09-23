import os
from subprocess import DEVNULL, check_call, CalledProcessError

from libs.cli.printer import Printer
from libs.cli.config import Config


class CMDConnect:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info("connect to the workstation")
            Printer.info("usage:")
            Printer.info("  connect")
            Printer.newline()
            return True
        else:
            Printer.newline()
            try:
                Printer.warning("You can use noVNC: http://{0}:6901".format(Config.get('WORKSTATION_IP')))
                if os.path.isfile(Config.get('VNC_CLIENT')):
                    check_call([Config.get('VNC_CLIENT'), '{0}:1'.format(Config.get('WORKSTATION_IP'))], stdout=DEVNULL, stderr=DEVNULL)
            except CalledProcessError:
                Printer.error('Error while launching VNC Client')
            Printer.newline()
            return True

    @staticmethod
    def help():
        return 'connect VNC to Workstation'
