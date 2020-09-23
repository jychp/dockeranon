from libs.cli.printer import Printer
from libs.cli.config import Config


class CMDShowConfig:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info('display the current configuration')
            Printer.newline()
            return True
        elif cmd == '':
            Printer.newline()
            for key, value in Config.get_all():
                Printer.kv(key, value)
            Printer.newline()
            return True
        else:
            Printer.error("Bad arguments. Use 'showconfig help' for more information.")
            return False

    @staticmethod
    def help():
        return 'display the current configuration'
