import os
import socket


class User:
    def __init__(self):
        try:
            self.name = os.environ["USER"]
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
