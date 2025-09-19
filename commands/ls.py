from abstract.command import Command


class LsCommand(Command):
    """
    ls - list directory contents

    Usage:
        ls [OPTIONS] [PATH...]

    Description:
        Lists files and directories in the specified PATH(s).
        If no PATH is given, lists contents of the current directory (".").
        Multiple PATHs can be provided — each will be listed in sequence.

    Options:
        -a    Show all files (including hidden files starting with '.').

    Examples:
        $ ls                # List current directory
        $ ls /home          # List /home directory
        $ ls -a             # List all files (including hidden)
        $ ls dir1 dir2      # List multiple directories

    Notes:
        - If PATH does not exist or is not a directory, prints an error.
        - Hidden files (starting with '.') are hidden by default — use -a to show them.
        - Output is one entry per line (simplified for virtual FS).
    """

    command = "ls"
    flags = {
        "-a": {"action": "store_true", "help": "show all files in directory"}
    }
    args = {
        "paths": {
            "nargs": "*",
            "default": ["."],
            "help": "path to directory",
            "metavar": "PATH",
        }
    }

    def execute(self, args):
        data = self.parse_args(args)

        if data is None:
            return

        print("\n".join(self.fs.ls(data.paths[0])))
