import argparse

from commands.register import Register
from commands import (
    CdCommand,
    LsCommand,
    ScCommand,
    HeadCommand,
    TacCommand,
    WcCommand,
    RmCommand,
)
from xml_parser import XmlClient
from user import User
from environment import Environment
from file_system import FileSystem
from terminal.terminal import Terminal
from terminal.interactive import InteractiveRunner


def parse_input(terminal: Terminal):
    """
    Parses command-line arguments and executes initial command if provided.

    Supports two key arguments:
        --vfs PATH      → Path to virtual filesystem XML file.
        --script PATH   → Path to script file to execute.

    If both are provided, executes: `sc --vfs {vfs} --script {script}`
    This allows "batch mode" startup without entering interactive shell.

    Args:
        terminal (Terminal): Terminal instance to execute the 'sc' command.

    Example:
        python main.py --vfs my_vfs.xml --script setup.txt
        → Executes script in virtual FS without entering REPL.
    """
    parser = argparse.ArgumentParser(
        description="Virtual Shell - Interactive terminal with virtual filesystem"
    )

    parser.add_argument("--vfs", help="Path to virtual filesystem XML file")
    parser.add_argument("--script", help="Path to script file to execute")

    args = parser.parse_args()

    # If both --vfs and --script provided → execute sc command immediately
    if args.vfs and args.script:
        try:
            terminal.process_line(
                f"sc --vfs {args.vfs} --script {args.script}"
            )
        except FileExistsError as e:
            print(e)


def initialize_system():
    """
    Initializes core system components: fs, user, env, register, terminal.

    Returns:
        tuple: (fs, user, env, register, terminal)
    """
    fs = FileSystem(XmlClient("vfs.xml").xml_dict)
    fs.create_file_system()

    user = User()
    env = Environment()

    register = Register(fs, user, env)
    terminal = Terminal(fs, user, env, register)
    register.terminal = terminal

    return fs, user, env, register, terminal


def register_commands(register: Register):
    """
    Registers all built-in commands.

    Args:
        register (Register): Command registry.
    """
    register.register("cd", CdCommand)
    register.register("ls", LsCommand)
    register.register("sc", ScCommand)
    register.register("head", HeadCommand)
    register.register("tac", TacCommand)
    register.register("wc", WcCommand)
    register.register("rm", RmCommand)


def main():
    """
    Main application entry point.

    Performs system initialization:
      1. Registers all built-in commands (cd, ls, sc, head, tac, wc, rm).
      2. Parses command-line arguments (for --vfs/--script mode).
      3. Starts interactive shell (REPL) if no script was executed.

    Note:
        Assumes global `terminal` and `register_command` are initialized before calling.
    """
    # Initialize system
    fs, user, env, register, terminal = initialize_system()

    # Register commands
    register_commands(register)

    # Handle --vfs/--script arguments (batch mode)
    parse_input(terminal)

    # Start interactive shell (REPL)
    runner = InteractiveRunner(terminal)
    runner.run()


if __name__ == "__main__":
    main()
