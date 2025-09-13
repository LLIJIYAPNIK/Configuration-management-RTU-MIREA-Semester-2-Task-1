from base.command import Command


class CdCommand(Command):
    """
    cd - change directory
    Usage:
        cd [path]
    Changes the current working directory to the specified path.
    If no path is specified, it changes to the home directory.

    Examples:
        cd
        cd /home/user
        cd ..
        cd ../..
    """
    command = "cd"
    command_description = "cd - change directory"

    def execute(self, *args):
        data = self.parser.parse_args(*args)
        print(data)
        return f"cd {' '.join(*args)}"

    def get_help(self):
        return self.__doc__.strip()
