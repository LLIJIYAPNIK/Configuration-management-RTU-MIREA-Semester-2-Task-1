from commands.register import Register
from environment import Environment
from exceptions import UnknownCommandName
from file_system import FileSystem
from user import User


class Terminal:
    def __init__(self, fs: FileSystem, user: User, env: Environment, register: Register):
        self.fs = fs
        self.user = user
        self.env = env
        self.register = register
        self.is_running = True

    def get_prompt(self):
        return self.user.get_user_for_shell(self.fs.cwd)

    def process_line(self, line: str):
        if not line.strip():
            return

        parts = line.split()
        command_name, *args = parts

        if command_name == "exit":
            self.is_running = False
            return

        if command_name in self.register.commands:
            self.register.execute(command_name, *args)
        elif command_name.startswith("$"):
            var = self.env.get(command_name[1:])
            print(var or "")
        else:
            raise UnknownCommandName(f"Unknown command: {command_name}")