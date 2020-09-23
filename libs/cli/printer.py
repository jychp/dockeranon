from prompt_toolkit import print_formatted_text, HTML


class Printer:

    @staticmethod
    def error(msg):
        print_formatted_text(HTML('<b><FireBrick>ERROR: {0}</FireBrick></b>'.format(msg)))

    @staticmethod
    def warning(msg):
        print_formatted_text(HTML('<DarkOrange>{0}</DarkOrange>'.format(msg)))

    @staticmethod
    def success(msg):
        print_formatted_text(HTML('<ForestGreen>{0}</ForestGreen>').format(msg))

    @staticmethod
    def info(msg):
        print_formatted_text(msg)

    @staticmethod
    def kv(key, value):
        print_formatted_text(HTML('<b>{0}:</b> {1}'.format(key, value)))

    @staticmethod
    def newline():
        print()
