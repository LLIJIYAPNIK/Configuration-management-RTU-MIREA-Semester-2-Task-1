import os

from abstract.command import Command
from commands import Register
from file_system import FileSystem
from terminal.script import ScriptRunner
from xml_parser import XmlClient


class ScCommand(Command):
    """
    sc - execute commands from a script file in a virtual filesystem

    Usage:
        sc --vfs PATH_TO_VFS --script PATH_TO_SCRIPT

    Description:
        Loads a virtual filesystem from XML file, then executes all commands
        from the specified script file in that isolated environment.

        This is useful for:
          - Testing commands in a controlled FS state.
          - Automating complex operations.
          - Running batch jobs in a sandbox.

    Options:
        --vfs PATH      Path to XML file defining the virtual filesystem.
        --script PATH   Path to script file containing commands (one per line).

    Examples:
        $ sc --vfs vfs.xml --script setup.txt
        $ sc --vfs /tmp/test_fs.xml --script /home/user/commands.sh

    Notes:
        - Both --vfs and --script are required.
        - Script file must exist and be readable.
        - VFS XML file must be valid and parseable.
        - After execution, the shell's filesystem is replaced with the new one.
        - All registered commands are available in the script environment.
    """

    command = "sc"
    command_description = "start script"
    flags = {
        "--vfs": {"type": str, "help": "path to vfs"},
        "--script": {"type": str, "help": "path to script"},
    }
    args = {}

    def execute(self, args):
        data = self.parse_args(args)

        if data is None:
            return

        if os.path.exists(data.vfs):
            new_file_system = FileSystem(XmlClient(data.vfs).xml_dict)
            new_file_system.create_file_system()
        else:
            raise FileExistsError("VFS not found. Check your path to VFS.")

        if os.path.exists(data.script):
            path_to_script = data.script
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
