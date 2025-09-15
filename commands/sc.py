import os

from base.command import Command
from file_system import FileSystem
from terminal import ScriptTerminal
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
            print(new_file_system is self.register.fs)
        else:
            raise FileExistsError("VFS not found. Check your path to VFS.")

        if os.path.exists(parsed.script):
            path_to_script = parsed.script
        else:
            raise FileExistsError("Script not found. Check your path to script.")

        with ScriptTerminal(new_file_system, self.register.user, self.register.env, self.register) as terminal:
            terminal.execute_script(path_to_script)

    def get_help(self):
        return self.__doc__.strip()
