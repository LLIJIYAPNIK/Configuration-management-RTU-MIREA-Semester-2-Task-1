from abstract.command import Command


class CdCommand(Command):
    """
    cd - change the current working directory

    Usage:
        cd [PATH]

    Description:
        Changes the shell's current working directory to the specified PATH.
        If PATH is not provided, defaults to the current directory (".").
        Supports relative paths, absolute paths, and ".." for parent directory.

    Special Paths:
        cd          → same as cd . (no change)
        cd ..       → go to parent directory
        cd ../..    → go up two levels
        cd /        → go to root directory

    Examples:
        $ cd /home/user
        $ cd ..
        $ cd projects/docs
        $ cd

    Notes:
        - If PATH does not exist or is not a directory, prints an error.
        - Does not support shell expansions (e.g., ~, $HOME) — use absolute/relative paths.
    """

    command = "cd"
    flags = {}
    args = {
        "path": {
            "nargs": "?",
            "default": ".",
            "help": "Target directory path (relative or absolute)",
            "metavar": "PATH",
        }
    }

    def execute(self, args):
        data = self.parse_args(args)
        if data is None:
            return

        try:
            self.fs.cd(data.path)
        except (ValueError, FileNotFoundError, NotADirectoryError) as e:
            print(f"cd: {e}")
