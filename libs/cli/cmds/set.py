from libs.cli.printer import Printer
from libs.cli.config import Config


class CMDSet:
    @staticmethod
    def exec(cmd):
        if cmd == 'help':
            Printer.newline()
            Printer.info("set a specific value of the configuration")
            Printer.info("usage:")
            Printer.info("  set var_name value")
            Printer.newline()
            return True
        elif cmd == '':
            Printer.error("Bad arguments. Use 'set help' for more information.")
            return False
        else:
            t = cmd.split(' ', 1)
            if len(t) != 2:
                Printer.error("Bad arguments. Use 'set help' for more information.")
                return False
            Config.set(t[0], t[1])
            return True

    @staticmethod
    def help():
        return 'set a specific value of the configuration'
