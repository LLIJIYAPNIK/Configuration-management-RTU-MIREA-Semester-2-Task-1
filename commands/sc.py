import os

from abstract.command import Command
from commands import Register
from file_system import FileSystem
from terminal.script import ScriptRunner
from xml_parser import XmlClient


class ScCommand(Command):
    """
    sc - start command

    Usage:
        sc --vfs [path/to/vfs] --script [path/to/script]
    Example:
        sc --vfs /home/user/vfs --script /home/user/script.py
    """

    command = "sc"
    command_description = "start script"
    flags = {
        "--vfs": {"type": str, "help": "path to vfs"},
        "--script": {"type": str, "help": "path to script"},
    }
    args = {}

    def execute(self, args):
        parsed = self.parser.parse_args(args)

        if os.path.exists(parsed.vfs):
            new_file_system = FileSystem(XmlClient(parsed.vfs).xml_dict)
            new_file_system.create_file_system()
        else:
            raise FileExistsError("VFS not found. Check your path to VFS.")

        if os.path.exists(parsed.script):
            path_to_script = parsed.script
        else:
            raise FileExistsError(
                "Script not found. Check your path to script."
            )

        new_register = Register(new_file_system, self.user, self.env)
        new_register.terminal = self.register.terminal
        for cmd_name, cmd_class in self.register.commands.items():
            new_register.commands[cmd_name] = cmd_class
            new_register.commands[cmd_name].fs = new_file_system

        self.register.terminal.fs = new_file_system
        self.register.terminal.register = new_register

        runner = ScriptRunner(self.register.terminal)
        runner.run(path_to_script)

    def get_help(self):
        return self.__doc__.strip()
