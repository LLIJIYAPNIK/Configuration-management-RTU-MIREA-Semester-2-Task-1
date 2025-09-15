from base import Command
from file_system.file_system import FileSystem


class Register:
    """Manages registration and execution of command classes."""

    def __init__(self, fs: FileSystem):
        """Initialize a new instance of RegisterCommand with an empty command registry."""
        self.commands = {}
        self.fs = fs

    def register(self, name: str, command_class: Command) -> None:
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
            self.commands[name].fs = self.fs

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
        obj = self.get(name)
        return obj().execute(args)
