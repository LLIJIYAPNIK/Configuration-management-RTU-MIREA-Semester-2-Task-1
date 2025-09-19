from abstract import Runner


class ScriptRunner(Runner):
    """
    Script-based command runner — executes commands from a script file line by line.

    This runner reads a text file containing shell commands (one per line),
    skips empty lines and comments (starting with '#'),
    and executes each command through the terminal.

    Features:
      - Prints prompt + command before execution (for transparency/logging).
      - Skips empty lines and comments (lines starting with '#').
      - Stops early if terminal.is_running becomes False (e.g., after "exit" command).
      - Reports line number on errors for easy debugging.
      - Gracefully handles missing script files.

    Example script file:
        # This is a comment
        cd /home/user
        ls

    Example usage:
        runner = ScriptRunner(terminal)
        runner.run("script.txt")

    Inheritance:
        Runner → ScriptRunner
    """

    def run(self, script_path: str):
        """
        Executes all valid commands from the specified script file.

        Processing rules:
          - Lines are stripped of whitespace.
          - Empty lines and lines starting with '#' are skipped.
          - Before executing each command, prints: "{prompt}{command}" (for visibility).
          - If terminal.is_running becomes False (e.g., via "exit"), stops immediately.
          - On error, prints: "Error on line {N}: {message}" — does not stop execution.
          - If file not found, prints error and exits.

        Args:
            script_path (str): Path to the script file to execute.

        This method does not return a value — it runs to completion or until error/file not found.
        """
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    # Respect terminal's running state (e.g., "exit" command stops execution)
                    if not self.terminal.is_running:
                        break

                    # Clean and validate line
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue  # Skip empty lines and comments

                    try:
                        # Print prompt + command for transparency (like a logged shell)
                        print(f"{self.terminal.get_prompt()}{line}")
                        # Execute the command
                        self.terminal.process_line(line)
                    except Exception as e:
                        # Log error with line number — continue with next line
                        print(f"Error on line {line_num}: {e}")
        except FileNotFoundError:
            # Gracefully handle missing script file
            print(f"Script file not found: {script_path}")
