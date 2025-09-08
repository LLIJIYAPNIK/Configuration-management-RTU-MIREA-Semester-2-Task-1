from user import User
from environment import Environment, VarEnvironmentNotFound
from command import RegisterCommand

from commands import CdCommand, LsCommand
from exceptions import UnknownCommandName


def main():
    env = Environment()
    user = User()

    register_command = RegisterCommand()
    register_command.register("cd", CdCommand)
    register_command.register("ls", LsCommand)

    while True:
        try:
            line = input(user.get_user_for_shell())

            cmd_name, *args = line.split()
            if cmd_name == "exit":
                break

            if cmd_name in register_command.commands:
                ans = register_command.execute(cmd_name, args)
                print(ans)
            elif cmd_name.startswith("$"):
                var = env.get(cmd_name[1:])
                print(var)
            else:
                raise UnknownCommandName(cmd_name)
        except VarEnvironmentNotFound(cmd_name) as e:
            raise e
        except KeyboardInterrupt as e:
            raise e
        except UnknownCommandName as e:
            raise e




if __name__ == '__main__':
    main()
