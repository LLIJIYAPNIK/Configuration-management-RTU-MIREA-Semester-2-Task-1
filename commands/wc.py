from abstract.command import Command


class WcCommand(Command):
    """
    wc - word, line, character, and longest line count

    Usage:
        wc [OPTIONS] PATH

    Description:
        Prints counts of lines, words, characters, and longest line length for a file.

        By default, prints: lines words characters filename
        Use flags to customize output.

    Options:
        -I    Print the number of lines.
        -w    Print the number of words.
        -m    Print the number of characters.
        -L    Print the length of the longest line.

    Examples:
        $ wc file.txt                    # Default: lines words chars filename
        $ wc -l file.txt                 # Only line count
        $ wc -w -m file.txt              # Words and characters
        $ wc -L file.txt                 # Longest line length
        $ wc -l -w -m -L file.txt        # All counts

    Notes:
        - PATH must point to an existing file (not a directory).
        - Words are defined as non-whitespace sequences (split by whitespace).
        - Lines are split by newline character — empty file has 1 line.
        - Characters include all bytes (including newlines).
        - Longest line is measured in characters (excluding newline).
    """

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

    def execute(self, args):
        data = self.parse_args(args)

        if data is None:
            return

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

    @staticmethod
    def get_word_count(file_content: str):
        """Count words by splitting on whitespace."""
        return len(file_content.split())

    @staticmethod
    def get_lines_count(file_content: str):
        """Count lines — split by newline. Empty string → 1 line."""
        return len(file_content.split("\n"))

    @staticmethod
    def get_symbols_count(file_content: str):
        """Count all characters (including newlines)."""
        return len(file_content)

    @staticmethod
    def get_max_length_line(file_content: str):
        """Return length of the longest line (excluding newline)."""
        return max(map(len, file_content.split("\n")))
