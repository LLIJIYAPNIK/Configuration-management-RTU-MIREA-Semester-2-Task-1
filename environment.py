import os


class VarEnvironmentNotFound(Exception):
    def __init__(self, var: str):
        self.var = var
        super().__init__(f"Variable {self.var} not found in environment")

class Environment:
    def __init__(self):
        self.environment_copy = os.environ.copy()

    def get(self, var: str) -> str | None:
        if var in self.environment_copy:
            return self.environment_copy[var]
        else:
            raise VarEnvironmentNotFound(var)

    def set(self, var: str, value: str) -> int():
        if var in self.environment_copy:
            self.environment_copy[var] = value
            return 0
        else:
            raise VarEnvironmentNotFound(var)
