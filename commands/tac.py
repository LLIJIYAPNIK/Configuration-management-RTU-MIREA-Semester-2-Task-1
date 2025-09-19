from abstract.command import Command


class TacCommand(Command):
    """
    tac - concatenate and print files in reverse

    Usage:
        tac PATH

    Description:
        Prints the contents of a file line by line, but in reverse order.
        The last line of the file is printed first, the first line — last.

        This is the reverse of the `cat` command — hence the name "tac".

    Examples:
        $ tac file.txt
        $ tac /path/to/file
        $ tac ../logs/error.log

    Notes:
        - PATH must point to an existing file (not a directory).
        - If file is empty, prints nothing.
        - If file does not exist, prints an error.
        - Preserves line endings — each line is printed as-is, just in reverse order.
    """

    command = "tac"
    command_description = "read file reverse"
    flags = {}
    args = {
        "path": {
            "nargs": "+",
            "help": "path to file",
            "metavar": "PATH",
        }
    }

    def execute(self, args):
        data = self.parse_args(args)

        if data is None:
            return

        if not self.register.fs.exists(data.path[0]):
            raise FileExistsError("File does not exists. Check your path.")

        print(
            "\n".join(
                self.register.fs.find(data.path[0]).read().split("\n")[::-1]
            )
        )
