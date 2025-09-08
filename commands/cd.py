from command import BaseCommand


class CdCommand(BaseCommand):
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
    def execute(self, *args):
        return f"cd {' '.join(args[0])}"

    def get_help(self):
        return self.__doc__.strip()
