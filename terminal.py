from commands.register import Register

from exceptions import UnknownCommandName
from user import User
from environment import Environment

from file_system import FileSystem


class Terminal:
    def __init__(
        self, fs: FileSystem, user: User, env: Environment, register: Register
    ):
        self.user = user
        self.env = env
        self.fs = fs
        self.register = register
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                line = input(self._get_prompt())
                self._process_line(line)
            except KeyboardInterrupt:
                print()
                break
            except EOFError:
                break
            except Exception as e:
                print(e)

    def _get_prompt(self):
        return self.user.get_user_for_shell(self.fs.cwd)

    def _process_line(self, line):
        if not line.strip():
            return

        parts = line.split()
        command_name = parts[0]
        args = parts[1:]

        if command_name == "exit":
            self.is_running = False
            return

        if command_name in self.register.commands:
            self.register.execute(command_name, *args)
        elif command_name.startswith("$"):
            var = self.env.get(command_name)
            print(var or "")
        else:
            raise UnknownCommandName(command_name)


class ScriptTerminal(Terminal):
    def __init__(self, fs, user, env, register):
        super().__init__(fs, user, env, register)
        self.fs = fs
        self.user = User()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _get_prompt(self):
        return self.user.get_user_for_shell(self.fs.cwd)

    def execute_script(self, script_path: str):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        print(f"{self._get_prompt()}{line}")
                        self._process_line(line)
                    except Exception as e:
                        print(f"Error on line {line_num}: {e}")
        except FileNotFoundError:
            print(f"Script file not found: {script_path}")
