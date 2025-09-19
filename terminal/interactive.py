from abstract.runner import Runner
from .terminal import UnknownCommandName


class InteractiveRunner(Runner):
    """
    Interactive command runner — provides a REPL (Read-Eval-Print Loop) interface.

    This runner reads commands line-by-line from standard input (stdin),
    processes them through the terminal, and continues until:
      - User sends EOF (Ctrl+D),
      - User triggers KeyboardInterrupt (Ctrl+C),
      - Terminal sets `is_running = False` (e.g., via "exit" command).

    Features:
      - Displays prompt before each input (via `terminal.get_prompt()`).
      - Gracefully handles unknown commands and general exceptions.
      - Prints newline on interrupt for clean UX.
      - Designed for interactive shell-like usage.

    Example:
        runner = InteractiveRunner(terminal)
        runner.run()  # Starts REPL: waits for user input until exit

    Inheritance:
        Runner → InteractiveRunner
    """

    def run(self):
        """
        Starts the interactive REPL loop.

        Loop continues while `self.terminal.is_running` is True.

        Behavior:
          - Displays prompt from `terminal.get_prompt()` before each input.
          - Reads line from stdin using `input()`.
          - Processes line via `terminal.process_line()`.
          - On Ctrl+C / Ctrl+D → prints newline and exits loop.
          - On UnknownCommandName → prints error message and continues.
          - On any other exception → prints error and continues.

        This method does not return a value — it runs until interrupted or exited.
        """
        while self.terminal.is_running:
            try:
                # Display prompt and wait for user input
                line = input(self.terminal.get_prompt())
                # Process the command line through terminal
                self.terminal.process_line(line)
            except (KeyboardInterrupt, EOFError):
                # User pressed Ctrl+C or Ctrl+D — exit gracefully
                print()  # Print newline for clean prompt exit
                break
            except UnknownCommandName as e:
                # Command not found — show error, continue loop
                print(e)
            except Exception as e:
                # Any other error — show it, but don't crash the shell
                print(e)
