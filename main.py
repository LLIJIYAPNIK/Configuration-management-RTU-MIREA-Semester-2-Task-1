from commands.register import Register

from commands import CdCommand, LsCommand
from exceptions import UnknownCommandName
from xml_parser import XmlClient
from user import User
from environment import Environment

from file_system import FileSystem


def main():
    fs = (FileSystem(XmlClient("test_vfs.xml").xml_dict))
    fs.create_file_system()
    user = User()
    env = Environment()

    register_command = Register(fs)
    register_command.register("cd", CdCommand)
    register_command.register("ls", LsCommand)

    while True:
        try:
            line = input(user.get_user_for_shell(fs.cwd))

            if not line:
                continue

            cmd_name, *args = line.split()
            if cmd_name == "exit":
                break

            if cmd_name in register_command.commands:
                register_command.execute(cmd_name, *args)
            elif cmd_name.startswith("$"):
                var = env.get(cmd_name[1:])
                print(var)
            else:
                raise UnknownCommandName(cmd_name)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            continue




if __name__ == '__main__':
    main()
