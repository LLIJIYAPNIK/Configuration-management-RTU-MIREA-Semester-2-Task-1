from commands.register import Register

from commands import CdCommand, LsCommand, ScCommand
from xml_parser import XmlClient
from user import User
from environment import Environment

from file_system import FileSystem
from terminal import Terminal


def main():
    fs = FileSystem(XmlClient("test_vfs.xml").xml_dict)
    fs.create_file_system()

    user = User()
    env = Environment()

    register_command = Register(fs, user, env)
    register_command.register("cd", CdCommand)
    register_command.register("ls", LsCommand)
    register_command.register("sc", ScCommand)

    terminal = Terminal(fs, user, env, register_command)
    terminal.run()


if __name__ == "__main__":
    main()
