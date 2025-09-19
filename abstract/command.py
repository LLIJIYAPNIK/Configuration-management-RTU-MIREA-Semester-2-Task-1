import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    """
    Abstract base class for all CLI commands in the system.

    All concrete command classes must inherit from this class and implement:
      - `execute()`: the main logic of the command.
      - `get_help()`: returns a help string for the command.

    On instantiation, the command automatically:
      - Creates an argument parser (`argparse.ArgumentParser`),
      - Registers flags and positional arguments defined in class attributes `flags` and `args`,
      - Prepares dependency injection slots (`fs`, `user`, `env`, `register`) — to be populated by `Register`.

    Class Attributes (to be overridden by subclasses):
        command (str): the command name (e.g., "ls", "cd", "head").
        command_description (str): brief description of the command (optional — defaults to class docstring).
        flags (dict): dictionary of optional flags in format:
            {
                "--flag": {
                    "action": "store_true" | "store" | etc.,
                    "type": data_type,
                    "default": default_value,
                    "help": "description of the flag"
                },
                "-f": { ... }
            }
        args (dict): dictionary of positional arguments in the same format.

    Instance Attributes (injected by Register on registration):
        fs: FileSystem instance.
        user: User instance.
        env: Environment instance.
        register: Register instance (for accessing other commands/context).

    Methods:
        execute(*args): abstract method — must contain command logic.
        get_help(): abstract method — must return help text.
        register_args(): registers arguments with argparse (called automatically in __init__).
    """

    command = ""
    flags = {}
    args = {}

    def __init__(self):
        # Dependency injection targets — will be set by Register
        self.register = None
        self.command_description = self.__doc__.strip()
        # Initialize argument parser
        self.parser = argparse.ArgumentParser()

        # Auto-register arguments
        self.register_args()

    @abstractmethod
    def execute(self, *args):
        """
        Execute the command logic.

        Must be implemented by subclasses.
        Receives unparsed CLI arguments (as list of strings).
        Uses self.parser to parse them.
        """
        pass

    def parse_args(self, args):
        """
        Parse arguments without exiting on --help.

        Overrides default argparse behavior to prevent sys.exit() on --help.
        Instead, prints help and returns None.
        """
        try:
            return self.parser.parse_args(args)
        except SystemExit:
            return None

    def register_args(self):
        """
        Register command-line arguments and flags with argparse.ArgumentParser.

        Uses class-level `args` and `flags` dictionaries to configure the parser.
        Called automatically during __init__.
        """
        self.parser = argparse.ArgumentParser(
            prog=self.command,
            description=self.command_description,
            add_help=True,
            exit_on_error=False,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Register positional arguments
        for arg_name, config in self.args.items():
            kwargs = {"help": config.get("help", "")}
            if "nargs" in config:
                kwargs["nargs"] = config["nargs"]
            if "default" in config:
                kwargs["default"] = config["default"]
            if "metavar" in config:
                kwargs["metavar"] = config["metavar"]
            if "type" in config:
                kwargs["type"] = config["type"]
            self.parser.add_argument(arg_name, **kwargs)

        # Register flags
        for flag, config in self.flags.items():
            # Normalize flag format: ensure it starts with '-' or '--'
            if not flag.startswith("--") and not flag.startswith("-"):
                flag = f"--{flag}"
            elif not flag.startswith("-"):
                flag = f"-{flag}"

            kwargs = {
                "action": config.get("action", "store"),
                "help": config.get("help", ""),
            }
            if "default" in config:
                kwargs["default"] = config["default"]
            if "type" in config:
                kwargs["type"] = config["type"]
            self.parser.add_argument(flag, **kwargs)
