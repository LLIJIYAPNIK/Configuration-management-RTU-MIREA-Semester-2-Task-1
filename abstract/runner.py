from abc import ABC, abstractmethod


class Runner(ABC):
    """
    Abstract base class for all command runners in the system.

    A Runner is responsible for executing a sequence of commands in a specific mode:
      - InteractiveRunner: reads commands from user input (stdin) in a REPL loop.
      - ScriptRunner: reads commands from a script file line by line.

    The Runner holds a reference to a Terminal instance, which provides:
      - Access to the filesystem, user, environment, and command registry.
      - Methods to process individual command lines.

    Subclasses must implement the `run()` method to define their specific execution logic.
    The `*args` parameter in `run()` allows flexibility — for example, ScriptRunner uses it
    to accept a script file path.

    Architecture:
        Terminal (session state) → Runner (execution strategy) → Commands (business logic)

    Example:
        runner = InteractiveRunner(terminal)
        runner.run()  # starts REPL

        runner = ScriptRunner(terminal)
        runner.run("script.txt")  # executes commands from file
    """

    def __init__(self, terminal):
        """
        Initialize the runner with a terminal session.

        Args:
            terminal (Terminal): The terminal context containing fs, user, env, and command registry.
                                 Acts as the "session" for all command executions.
        """
        self.terminal = terminal

    @abstractmethod
    def run(self, *args):
        """
        Execute the command sequence according to the runner's strategy.

        Must be implemented by subclasses.

        Args:
            *args: Variable arguments to support different runner types.
                   Example: ScriptRunner expects a script file path as the first argument.

        Behavior varies by subclass:
          - InteractiveRunner: starts a REPL loop, reads from stdin until exit.
          - ScriptRunner: reads and executes commands from a file.
        """
        pass
