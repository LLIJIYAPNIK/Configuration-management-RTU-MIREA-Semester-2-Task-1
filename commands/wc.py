from abstract.command import Command


class WcCommand(Command):
    """word count"""

    command = "wc"
    command_description = "word count"
    flags = {
        "-I": {
            "action": "store_true",
            "help": "show quantity of lines of file",
        },
        "-w": {
            "action": "store_true",
            "help": "show quantity of words of file",
        },
        "-m": {
            "action": "store_true",
            "help": "show quantity of symbols of file",
        },
        "-L": {
            "action": "store_true",
            "help": "show the longest line in the file",
        },
    }
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

        file = self.register.fs.find(data.path[0])
        file_str = file.read()

        word_count = self.get_word_count(file_str)
        lines_count = self.get_lines_count(file_str)
        symbols_count = self.get_symbols_count(file_str)
        max_len_line = self.get_max_length_line(file_str)

        if not any([data.I, data.w, data.m, data.L]):
            print(f"{lines_count} {word_count} {symbols_count} {file.name}")
        else:
            result = ""

            if data.w:
                result += f"{word_count} "
            if data.I:
                result += f"{lines_count} "
            if data.m:
                result += f"{symbols_count} "
            if data.L:
                result += f"{max_len_line} "

            print(result + file.name)

    def get_help(self):
        return self.__doc__.strip()

    @staticmethod
    def get_word_count(file_content: str):
        return len(file_content.split())

    @staticmethod
    def get_lines_count(file_content: str):
        return len(file_content.split("\n"))

    @staticmethod
    def get_symbols_count(file_content: str):
        return len(file_content)

    @staticmethod
    def get_max_length_line(file_content: str):
        return max(map(len, file_content.split("\n")))
