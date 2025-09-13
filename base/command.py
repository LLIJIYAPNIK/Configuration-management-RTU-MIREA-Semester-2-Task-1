import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    command = ""
    command_description = ""
    flags = {}
    args = {}

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.command_description = self.__doc__

        self.register_args()

    @abstractmethod
    def execute(self, *args):
        """Execute the command.

        This method must be implemented by subclasses.
        """

    @abstractmethod
    def get_help(self):
        """Get help for the command.

        This method must be implemented by subclasses.
        """

    def register_args(self):
        self.parser = argparse.ArgumentParser(
            prog=self.command,
            description=self.command_description,
            add_help=True,
            exit_on_error=False
        )

        for arg_name, config in self.args.items():
            kwargs = {
                "help": config.get("help", ""),
            }

            if "nargs" in config:
                kwargs["nargs"] = config["nargs"]

            if "default" in config:
                kwargs["default"] = config["default"]

            if "metavar" in config:
                kwargs["metavar"] = config["metavar"]

            self.parser.add_argument(arg_name, **kwargs)

        for flag, config in self.flags.items():
            kwargs = {
                "action": config.get("action", "store"),
                "help": config.get("help", ""),
            }

            if "default" in config:
                kwargs["default"] = config["default"]

            self.parser.add_argument(flag, **kwargs)
