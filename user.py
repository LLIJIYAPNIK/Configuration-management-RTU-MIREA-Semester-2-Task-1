import socket
import getpass

from abstract.file_system_object import FileSystemObject


class User:
    """
    Represents the current user and host context for shell prompt generation.

    Provides dynamic shell prompts in the format:
        "{username}@{hostname}:~{current_path}$ "

    Automatically detects real system username and hostname if not provided.
    Fully customizable — can be overridden for testing or virtual sessions.

    Example:
        user = User()                          # → Uses real system user/hostname
        user = User("admin", "server")         # → Forces custom values
        print(user)                            # → "admin@server"
        print(user.get_user_for_shell(cwd))    # → "admin@server:~/home/docs$ "

    Attributes:
        name (str): Username (defaults to system user via getpass.getuser()).
        hostname (str): Hostname (defaults to system hostname via socket.gethostname()).
    """

    def __init__(self, name=None, hostname=None):
        """
        Initializes user context with optional overrides.

        Args:
            name (str, optional): Username. If None, auto-detects via getpass.getuser().
            hostname (str, optional): Hostname. If None, auto-detects via socket.gethostname().

        Note:
            Auto-detection uses real system values — useful for "native" shell feel.
            Override for testing, containers, or virtual environments.
        """
        self.name = (
            getpass.getuser() if name is None else name
        )  # Thank you to Elizaveta Beltiukova for this tip
        self.hostname = socket.gethostname() if hostname is None else hostname

    def get_user_for_shell(self, cwd: FileSystemObject) -> str:
        """
        Generates a shell-style prompt string for the current working directory.

        Format: "{username}@{hostname}:~{absolute_path}$ "

        Example outputs:
            "alice@laptop:~/home/projects$ "
            "root@server:~/etc/config$ "

        Args:
            cwd (FileSystemObject): Current working directory object.

        Returns:
            str: Formatted prompt string ready for display in shell.
        """
        return f"{str(self)}:~{cwd.get_absolute_path()}$ "

    def __str__(self) -> str:
        """
        Returns the user@host string representation.

        Used in prompt generation and for debugging.

        Returns:
            str: "{name}@{hostname}"
        """
        return f"{self.name}@{self.hostname}"
