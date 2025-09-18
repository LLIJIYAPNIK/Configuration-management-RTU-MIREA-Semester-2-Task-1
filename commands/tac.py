from abstract.command import Command


class TacCommand(Command):
    """read file reverse"""

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

    def execute(self, *args):
        data = self.parser.parse_args(*args)

        if not self.register.fs.exists(data.path[0]):
            raise FileExistsError("File does not exists. Check your path.")

        print(
            "\n".join(
                self.register.fs.find(data.path[0]).read().split("\n")[::-1]
            )
        )

    def get_help(self):
        return self.__doc__.strip()
