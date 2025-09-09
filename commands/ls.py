from command import BaseCommand


class LsCommand(BaseCommand):
    """
    ls - list files
    Usage:
        ls
        ls [path]
    Example:
        ls
        ls /
        ls ~/path/to/file
    """

    command = "ls"
    command_description = "list files"
    flags = {
        "-a": {
            "action": "store_true",
            "help": "show all files in directory"
        }
    }
    args = {
        "paths": {
            "nargs": "*",
            "default": ["."],
            "help": "path to directory",
            "metavar": "PATH"
        }
    }

    def execute(self, raw_args):
        return f"ls {' '.join(raw_args)}"

    def get_help(self):
        return self.__doc__.strip()
