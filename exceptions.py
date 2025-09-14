class BaseCommandException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class UnknownCommandName(BaseCommandException):
    def __init__(self, command_name: str):
        super().__init__(command_name)
        self.message = f"Unknown command: {command_name}"
