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
    # Register all available commands
    register_command.register("cd", CdCommand)
    register_command.register("ls", LsCommand)
    register_command.register("sc", ScCommand)
    register_command.register("head", HeadCommand)
    register_command.register("tac", TacCommand)
    register_command.register("wc", WcCommand)
    register_command.register("rm", RmCommand)

    # Handle --vfs/--script arguments (batch mode)
    parse_input(terminal)

    # Start interactive shell (REPL)
    runner = InteractiveRunner(terminal)
    runner.run()


if __name__ == "__main__":
    """
    Application bootstrap — creates core system components and starts main().

    Initialization sequence:
      1. Load virtual filesystem from 'vfs.xml'
      2. Create User (auto-detects system user/hostname)
      3. Create Environment (copies real OS env for isolation)
      4. Create Register (command registry)
      5. Create Terminal (session context)
      6. Link Register → Terminal (for command access)
      7. Call main() → register commands, parse args, start shell

    Default behavior:
        - Loads 'vfs.xml' from current directory.
        - Starts interactive shell after processing --vfs/--script (if any).

    Example runs:
        python main.py                          → Interactive shell
        python main.py --vfs test.xml --script init.txt → Run script, then exit
    """
    # Load virtual filesystem from XML
    fs = FileSystem(XmlClient("vfs.xml").xml_dict)
    fs.create_file_system()

    # Create user context (auto-detects real system user/hostname)
    user = User()

    # Create isolated environment (copies real OS env)
    env = Environment()

    # Create command registry
    register_command = Register(fs, user, env)

    # Create terminal session
    terminal = Terminal(fs, user, env, register_command)

    # Link terminal back to register (for command access to terminal)
    register_command.terminal = terminal

    # Start application
    main()
