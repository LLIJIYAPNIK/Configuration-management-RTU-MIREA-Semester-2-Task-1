from abstract.command import Command
from file_system import Directory


class HeadCommand(Command):
    """
    head - display the first N lines of a file

    Usage:
        head [OPTIONS] PATH

    Description:
        Prints the first N lines of the specified file.
        By default, shows the first 10 lines.
        If the file has fewer lines, prints all available lines.

    Options:
        -n N    Number of lines to display (default: 10)

    Examples:
        $ head file.txt           # Show first 10 lines
        $ head -n 5 file.txt      # Show first 5 lines
        $ head -n 0 file.txt      # Error: N must be > 0
        $ head /path/to/file      # Absolute path
        $ head ../file.txt        # Relative path

    Notes:
        - PATH must point to a file (not a directory).
        - If file does not exist, prints an error.
        - If N <= 0, prints an error.
        - Empty file → prints nothing (but shows filename).
    """

    command = "head"
    flags = {
        "-n": {"type": int, "default": 10, "help": "Number of lines to show"}
    }
    args = {
        "path": {
            "nargs": "+",
            "help": "Path to the target file (supports relative/absolute paths)",
            "metavar": "PATH",
        }
    }

    def execute(self, args):
        data = self.parse_args(args)
        if data is None:
            return

        if not self.register.fs.exists(data.path[0]):
            raise FileExistsError("File does not exists. Check your path.")

        obj = self.register.fs.find(data.path[0])
        if isinstance(obj, Directory):
            raise TypeError("Object have to be a File, not a Directory")

        if data.n <= 0:
            raise ValueError(
                f"Number have to be more than 0. Your n: {data.n}"
            )

        # Print filename and first N lines
        print(obj.name)
        lines = obj.read().split("\n")
        print("\n".join(lines[: data.n]))
