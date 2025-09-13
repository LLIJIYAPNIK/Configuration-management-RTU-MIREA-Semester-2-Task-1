from typing import Optional

from abc import ABC, abstractmethod
from file_system.directory import Directory
from file_system.file import File


class FileSystemObject(ABC):
    """Abstract base class for all filesystem objects (files and directories)."""

    def __init__(self, name: str, parent: Optional['Directory'] = None):
        """
        Initializes a filesystem object.

        Args:
            name (str): Name of the object.
            parent (Directory, optional): Parent directory. Defaults to None.

        Raises:
            ValueError: If name is empty.
        """
        if not name:
            raise ValueError("Name cannot be empty")
        self.name = name
        self.parent = parent

    def get_absolute_path(self) -> str:
        """
        Returns the absolute path of this object.

        Returns:
            str: Absolute path starting with '/'.
        """
        if self.parent:
            parent_path = self.parent.get_absolute_path()
            if parent_path == "/":
                return f"/{self.name}"
            return f"{parent_path}/{self.name}"
        return self.name

    def rename(self, new_name: str) -> None:
        """
        Renames the object.

        Args:
            new_name (str): New name.

        Raises:
            ValueError: If new_name is empty.
        """
        if not new_name:
            raise ValueError("New name cannot be empty")
        self.name = new_name

    def is_dir(self) -> bool:
        """Returns True if this object is a Directory."""
        return isinstance(self, Directory)

    def is_file(self) -> bool:
        """Returns True if this object is a File."""
        return isinstance(self, File)

    def validate_clone(self, new_parent: 'Directory') -> None:
        """
        Validates parameters for cloning.

        Args:
            new_parent (Directory): New parent directory.

        Raises:
            ValueError: If new_parent is None or self.
            TypeError: If new_parent is not a Directory.
        """
        if not new_parent:
            raise ValueError("New parent cannot be empty")
        if not isinstance(new_parent, Directory):
            raise TypeError("New parent must be a Directory")
        if new_parent == self:
            raise ValueError("New parent cannot be the same as current directory")

    @abstractmethod
    def clone(self, new_parent: 'Directory') -> 'FileSystemObject':
        """
        Creates a deep copy of this object under a new parent.

        Args:
            new_parent (Directory): The directory where the clone will be placed.

        Returns:
            FileSystemObject: The cloned object.
        """
        pass
