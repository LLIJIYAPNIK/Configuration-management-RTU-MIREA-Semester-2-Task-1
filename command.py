from abc import abstractmethod, ABC


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
    """Base class for all commands.

    Attributes:
        args (tuple): Arguments passed to the command.
        description (str, optional): Description of the command.
    """

    VALID_FLAGS: dict[str, bool] = {}
    LONG_FLAGS: dict[str, str] = {}

    def __init__(self, args: list):
        self.args = args
        self.flags = {}
        self.positional = []

        self._parse()

    def _parse(self):
        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg == '--':
                self.positional.extend(self.args[i + 1:])
                break

            elif arg.startswith('--'):
                i = self._parse_long_flag(i)

            elif arg.startswith('-') and len(arg) > 1:
                i = self._parse_short_flags(i)

            else:
                self.positional.append(arg)

            i += 1

    def _parse_long_flag(self, i: int) -> int:
        part = self.args[i][2:]

        if '=' in part:
            long_name, value = part.split('=', 1)
        else:
            long_name, value = part, None

        if long_name not in self.LONG_FLAGS:
            raise UnknownFlagError(f"--{long_name}")

        short_name = self.LONG_FLAGS[long_name]
        takes_arg = self.VALID_FLAGS.get(short_name, False)

        if takes_arg:
            if value is not None:
                self.flags[short_name] = value
            else:
                if i + 1 >= len(self.args):
                    raise MissingArgumentError(f"--{long_name}")
                self.flags[short_name] = self.args[i + 1]
                return i + 1
        else:
            if value is not None:
                raise CommandParseError(f"--{long_name} does not accept an argument")
            self.flags[short_name] = True

        return i

    def _parse_short_flags(self, i: int) -> int:
        flag_group = self.args[i][1:]  # -lah → 'lah'

        j = 0
        while j < len(flag_group):
            flag = flag_group[j]

            if flag not in self.VALID_FLAGS:
                raise UnknownFlagError(f"-{flag}")

            takes_arg = self.VALID_FLAGS[flag]

            if not takes_arg:
                self.flags[flag] = True
                j += 1
                continue

            if j < len(flag_group) - 1:
                self.flags[flag] = flag_group[j + 1:]
                break
            else:
                if i + 1 >= len(self.args):
                    raise MissingArgumentError(f"-{flag}")
                self.flags[flag] = self.args[i + 1]
                return i + 1

            j += 1

        return i

    @abstractmethod
    def execute(self):
        """Execute the command.

        This method must be implemented by subclasses.
        """

    @abstractmethod
    def get_help(self):
        """Get help for the command.

        This method must be implemented by subclasses.
        """


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
            return self.commands[name].execute(*args)
        else:
            raise ValueError(f"Command {name} not found")
