import socket
import getpass

from base import FileSystemObject


class User:
    def __init__(self, name=None, hostname=None):
        self.name = (
            (
                getpass.getuser()  # Thank you to Elizaveta Beltiukova for this tip
            )
            if name is None
            else name
        )
        self.hostname = socket.gethostname() if hostname is None else hostname

    def get_user_for_shell(self, cwd: FileSystemObject):
        return f"{str(self)}:~{cwd.get_absolute_path()}$ "

    def __str__(self):
        return f"{self.name}@{self.hostname}"
