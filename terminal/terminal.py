from commands.register import Register
from environment import Environment
from file_system import FileSystem
from user import User


class UnknownCommandName(Exception):
    """
    Exception raised when a command name is not registered in the system.

    This exception is typically caught by the terminal or runner to display
    a user-friendly error message without crashing the shell.

    Attributes:
        command_name (str): The unrecognized command name that triggered the exception.
        message (str): Human-readable error message (e.g., "Unknown command: rm").

    Example:
        raise UnknownCommandName("rm")
        # → UnknownCommandName: Unknown command: rm
    """

    def __init__(self, command_name: str):
        super().__init__(command_name)
        self.message = f"Unknown command: {command_name}"


class Terminal:
    """
    The terminal session controller — the central runtime context for command execution.

    Acts as the "shell" that:
      - Maintains session state (filesystem, user, environment, command registry),
      - Generates interactive prompts via User,
      - Parses and routes command lines to appropriate handlers.

    Key Responsibilities:
      - Prompt Generation: Delegates to `user.get_user_for_shell(cwd)` for dynamic prompts.
      - Command Routing:
          - Built-in "exit" → terminates session.
          - Registered commands → delegates to Register.execute().
          - Environment variables ($VAR) → expands from Environment.
          - Unknown commands → raises UnknownCommandName.

    This class is stateful:
      - `is_running` controls whether the shell should continue (used by runners).
      - `fs.cwd` changes as user navigates filesystem.
      - `env` can be modified by commands (e.g., export, set).

    Example:
        terminal = Terminal(fs, user, env, register)
        terminal.process_line("ls")   # → executes 'ls' command
        terminal.process_line("$USER")    # → prints environment variable
        terminal.process_line("exit")     # → sets is_running = False
    """

    def __init__(
        self, fs: FileSystem, user: User, env: Environment, register: Register
    ):
        """
        Initializes a terminal session with all required context.

        Args:
            fs (FileSystem): The virtual filesystem (provides cwd, tree operations).
            user (User): User info for prompt generation and permissions.
            env (Environment): Key-value store for environment variables.
            register (Register): Command registry — maps names to command classes.

        Sets:
            is_running (bool): True by default — set to False to terminate session (e.g., via "exit").
        """
        self.fs = fs
        self.user = user
        self.env = env
        self.register = register
        self.is_running = True

    def get_prompt(self) -> str:
        """
        Generates the current shell prompt string.

        Delegates to User.get_user_for_shell(cwd) — typically returns strings like:
          - "user@host:~/project$ "
          - "admin@server:~/etc# "

        Returns:
            str: The formatted prompt string for the current working directory.
        """
        return self.user.get_user_for_shell(self.fs.cwd)

    def process_line(self, line: str) -> None:
        """
        Parses and executes a single command line.

        Processing pipeline:
          1. Strips whitespace — empty lines are ignored.
          2. Splits into command_name and args.
          3. Handles special cases:
               - "exit" → sets is_running = False.
               - "$VAR" → expands environment variable.
               - Registered command → delegates to Register.execute().
               - Unknown command → raises UnknownCommandName.

        Args:
            line (str): Raw command line from user or script.

        Raises:
            UnknownCommandName: If command is not registered and not a variable.

        Example:
            process_line("cd /home")   → executes 'cd' command
            process_line("$PATH")      → prints value of PATH variable
            process_line("exit")       → sets is_running = False
        """
        # Ignore empty/whitespace-only lines
        if not line.strip():
            return

        # Split into command and arguments
        parts = line.split()
        command_name, *args = parts

        # Handle built-in exit command
        if command_name == "exit":
            self.is_running = False
            return

        # Handle environment variable expansion (e.g., $USER)
        if command_name.startswith("$"):
            var_name = command_name[1:]
            var_value = self.env.get(var_name)
            print(var_value or "")  # Print empty string if variable not set
            return

        # Handle registered commands
        if command_name in self.register.commands:
            self.register.execute(command_name, *args)
            return

        # Handle unknown commands
        raise UnknownCommandName(f"Unknown command: {command_name}")
