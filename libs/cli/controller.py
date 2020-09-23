from .cmds import *

from .printer import Printer


class CLIController:
    KEEP_RUNNING = True
    _CMDS = {'showconfig': CMDShowConfig,
             'set': CMDSet,
             'launch': CMDLaunch,
             'status': CMDStatus,
             'exit': CMDExit,
             'connect': CMDConnect,
             'savegateway': CMDSaveGateway}

    def __init__(self, raw_cmd):
        self.raw_cmd = raw_cmd

    def exec(self):
        args = self.raw_cmd.split(" ", 1)
        if args[0] == 'help':
            Printer.newline()
            for cmd, cmd_class in self._CMDS.items():
                Printer.kv(cmd, cmd_class.help())
            Printer.newline()
        elif args[0] in self._CMDS:
            if len(args) > 1:
                self._CMDS[args[0]].exec(args[1])
            else:
                self._CMDS[args[0]].exec('')
        else:
            Printer.error("Unknown command, type 'help' for more information.")
