from abstract.command import Command


class RmCommand(Command):
    """
    rm - remove files or directories

    Usage:
        rm [PATH]

    Description:
        Removes the specified file or directory from the virtual filesystem.
        If PATH is not provided, defaults to current directory ("."), but this will fail
        (removing current directory is not allowed in most shells).

    Examples:
        $ rm file.txt           # Remove a file
        $ rm /path/to/file      # Remove using absolute path
        $ rm ../old_file.txt    # Remove using relative path
        $ rm empty_dir/         # Remove an empty directory
        $ rm nonempty_dir/      # Remove a directory with contents (if supported)

    Notes:
        - If PATH does not exist, prints an error.
        - If PATH is a directory, removes it and all its contents (recursive delete).
        - Removing root directory ("/") or current directory (".") is not allowed — prints error.
        - No confirmation prompt — deletion is immediate (like Unix rm without -i).
    """

    command = "rm"
    command_description = "rm - remove"
    flags = {}
    args = {
        "path": {
            "nargs": "?",
            "default": ".",
            "help": "path to directory",
            "metavar": "PATH",
        }
    }

    def execute(self, args):
        data = self.parse_args(args)

        if data is None:
            return

        self.fs.rm(data.path[0])
