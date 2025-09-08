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
    VALID_FLAGS = {
        'l': False,  # long format
        'a': False,  # all (include hidden)
        'h': False,  # human-readable
        'o': True,   # output to file
    }
    LONG_FLAGS = {
        'all': 'a',
        'long': 'l',
        'human-readable': 'h',
        'output': 'o',
    }

    def execute(self, *args):
        print(self.positional)
        print(self.flags)
        return f"ls {args}"

    def get_help(self):
        return self.__doc__.strip()
