from abc import abstractmethod, ABC
import argparse


class CommandParseError(Exception):
    """Базовое исключение для ошибок парсинга"""
    pass

class UnknownFlagError(CommandParseError):
    def __init__(self, flag: str):
        super().__init__(f"unknown option '{flag}'")

class MissingArgumentError(CommandParseError):
    def __init__(self, flag: str):
        super().__init__(f"option '{flag}' requires an argument")


class BaseCommand(ABC):
    command = ""
    command_description = ""
    flags = {}
    args = {}

    def __init__(self):
        self.parser = None
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


class RegisterCommand:
    """Manages registration and execution of command classes."""

    def __init__(self):
        """Initialize a new instance of RegisterCommand with an empty command registry."""
        self.commands = {}

    def register(self, name: str, command_class) -> None:
        """Register a command class under a given name.

        Args:
            name (str): Name of the command.
            command_class (BaseCommand): Command class to register.

        Raises:
            ValueError: If the command name is already registered.
        """
        if name in self.commands:
            raise ValueError(f"Command {name} already registered")
        else:
            self.commands[name] = command_class

    def get(self, name: str):
        """Retrieve a registered command class by name.

        Args:
            name (str): Name of the command.

        Returns:
            BaseCommand: The registered command class.

        Raises:
            ValueError: If the command name is not found.
        """
        if name in self.commands:
            return self.commands[name]
        else:
            raise ValueError(f"Command {name} not found")

    def execute(self, name: str, *args):
        """Execute a registered command with provided arguments.

        Args:
            name (str): Name of the command.
            *args: Arguments to pass to the command's execute method.

        Returns:
            Any: Result of the command's execute method.

        Raises:
            ValueError: If the command name is not found.
        """
        if name in self.commands:
            return self.commands[name]().execute(args)
        else:
            raise ValueError(f"Command {name} not found")
