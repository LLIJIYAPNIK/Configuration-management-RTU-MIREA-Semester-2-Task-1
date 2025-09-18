import argparse

from commands.register import Register

from commands import (
    CdCommand,
    LsCommand,
    ScCommand,
    HeadCommand,
    TacCommand,
    WcCommand,
)
from xml_parser import XmlClient
from user import User
from environment import Environment

from file_system import FileSystem
from terminal.terminal import Terminal
from terminal.interactive import InteractiveRunner


def parse_input(terminal: Terminal):
    parser = argparse.ArgumentParser()

    parser.add_argument("--vfs")
    parser.add_argument("--script")

    args = parser.parse_args()

    if args.vfs and args.script:
        try:
            terminal.process_line(
                f"sc --vfs {args.vfs} --script {args.script}"
            )
        except FileExistsError as e:
            print(e)


def main():
    register_command.register("cd", CdCommand)
    register_command.register("ls", LsCommand)
    register_command.register("sc", ScCommand)
    register_command.register("head", HeadCommand)
    register_command.register("tac", TacCommand)
    register_command.register("wc", WcCommand)
    parse_input(terminal)
    runner = InteractiveRunner(terminal)
    runner.run()


if __name__ == "__main__":
    fs = FileSystem(XmlClient("vfs.xml").xml_dict)
    fs.create_file_system()

    user = User()
    env = Environment()

    register_command = Register(fs, user, env)
    terminal = Terminal(fs, user, env, register_command)
    register_command.terminal = terminal

    main()
