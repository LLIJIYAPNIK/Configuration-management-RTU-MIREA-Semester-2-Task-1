import os


class VarEnvironmentNotFound(Exception):
    """
    Exception raised when attempting to access an undefined environment variable.

    Attributes:
        var (str): The name of the variable that was not found.
    """

    def __init__(self, var: str):
        self.var = var
        super().__init__(f"Variable {self.var} not found in environment")


class Environment:
    """
    Virtual environment manager — provides isolated access to environment variables.

    By default, initializes with a **copy** of the real OS environment (os.environ.copy()),
    ensuring all modifications stay within the virtual session and do not affect the host system.

    Supports:
      - Safe reading of variables (raises VarEnvironmentNotFound if not set).
      - Setting/updating variables.
      - Complete isolation from host environment.

    Example:
        env = Environment()  # Copies real OS env
        env = Environment({"USER": "test", "HOME": "/tmp"})  # Custom initial state

        env.set("DEBUG", "1")
        print(env.get("DEBUG"))  # → "1"
    """

    def __init__(self, from_user: dict = None):
        """
        Initializes the virtual environment.

        Args:
            from_user (dict, optional): Initial variable mapping.
                                      If None, copies real OS environment (os.environ.copy()).
        """

        self.environment = (
            from_user if from_user is not None else os.environ.copy()
        )

    def get(self, var: str) -> str | None:
        """
        Retrieves the value of an environment variable.

        Args:
            var (str): Variable name.

        Returns:
            str: Value of the variable.

        Raises:
            VarEnvironmentNotFound: If variable is not defined in this environment.
        """
        if var in self.environment:
            return self.environment[var]
        else:
            raise VarEnvironmentNotFound(f"{var} not found in environment")

    def set(self, var: str, value: str) -> int():
        """
        Sets or updates an environment variable.

        If the variable exists — updates its value.
        If it doesn't exist — creates it.

        Args:
            var (str): Variable name.
            value (str): Value to assign.

        Returns:
            str: "Success" on successful set/update.

        Note:
            Does not raise an error if variable didn't exist — creates it silently.
        """

        if self.get(var):
            self.environment[var] = value
            return "Success"
