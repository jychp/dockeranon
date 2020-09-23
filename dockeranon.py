#!/usr/bin/env python3
from prompt_toolkit import PromptSession
from prompt_toolkit import HTML
import docker
from requests.exceptions import ConnectionError

from libs.cli.controller import CLIController
from libs.cli.config import Config
from libs.cli.printer import Printer

from libs.builder import WorkstationBuilder, GatewayBuilder, NetworkBuilder


def main():
    session = PromptSession()
    # Tests
    try:
        client = docker.from_env()
        client.containers.list()
    except ConnectionError:
        Printer.error('Your current user are not allowed to use docker.')
        exit(1)
    # Main loop
    while Config.KEEP_RUNNING:
        try:
            text = session.prompt(HTML('<seagreen>DockerAnon</seagreen> > '))
            c = CLIController(text)
            c.exec()
        except KeyboardInterrupt:
            continue
        except Exception as e:
            WorkstationBuilder.clean()
            GatewayBuilder.clean()
            NetworkBuilder.clean()
            raise e


if __name__ == '__main__':
    main()
