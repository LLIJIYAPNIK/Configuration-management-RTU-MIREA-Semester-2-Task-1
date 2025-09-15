import os


class VarEnvironmentNotFound(Exception):
    def __init__(self, var: str):
        self.var = var
        super().__init__(f"Variable {self.var} not found in environment")


class Environment:
    def __init__(self, from_user: dict = None):
        self.environment = (
            from_user if from_user is not None else os.environ.copy()
        )

    def get(self, var: str) -> str | None:
        if var in self.environment:
            return self.environment[var]
        else:
            raise VarEnvironmentNotFound(f"{var} not found in environment")

    def set(self, var: str, value: str) -> int():
        if self.get(var):
            self.environment[var] = value
            return "Success"
