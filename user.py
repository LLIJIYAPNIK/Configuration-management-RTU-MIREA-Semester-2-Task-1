import os
import socket
import getpass


class User:
    def __init__(self):
        try:
            self.name = getpass.getuser()  # Thank you to Elizaveta Beltiukova for this tip
            self.hostname = socket.gethostname()
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def _get_cur_dir():
        return os.getcwd()

    def get_user_for_shell(self):
        return f"{str(self)}:{self._get_cur_dir()}$ "

    def __str__(self):
        return f"{self.name}@{self.hostname}"

    def __repr__(self):
        return f"{self.name}@{self.hostname}"
