from abstract.command import Command


class HeadCommand(Command):
    """
    head - show n rows of the file

    Usage:
        head path/to/your/file
        head -n path/to/your/file
    Example:
        head path/to/your/file - show first 10 rows
        head -n path/to/your/file - show first n rows
    """

    command = "head"
    command_description = "show 10/n first rows of the file"
    flags = {"-n": {"type": int, "default": 10, "help": "show first n rows"}}
    args = {
        "path": {
            "nargs": "+",
            "help": "path to file",
            "metavar": "PATH",
        }
    }

    def execute(self, *args):
        data = self.parser.parse_args(*args)
        print(data.n)
        if not self.register.fs.exists(data.path[0]):
            raise FileExistsError("File does not exists. Check your path.")

        if data.n <= 0:
            raise ValueError(
                f"Number have to be more than 0. Your n: {data.n}"
            )

        file = self.register.fs.find(data.path[0])
        print(file.name)
        print("\n".join(file.read().split("\n")[: data.n]))

    def get_help(self):
        return self.__doc__.strip()
