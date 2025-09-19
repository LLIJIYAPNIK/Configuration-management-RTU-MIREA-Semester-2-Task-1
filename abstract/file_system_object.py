from abc import ABC, abstractmethod


class FileSystemObject(ABC):
    """
    Abstract base class for all virtual filesystem objects — Files and Directories.

    This class defines the common interface and shared behavior for all items in the
    virtual filesystem, including:
      - Name and parent reference management
      - Absolute path calculation
      - Renaming
      - Validation for cloning operations
      - Abstract clone() method for deep copying

    All filesystem objects must have a non-empty name and may optionally belong to a parent.
    Root directory typically has no parent and name '/'.

    Inheritance:
        File: Represents a leaf node with content.
        Directory: Represents a container that can hold other FileSystemObjects.
    """

    def __init__(self, name: str, parent: "FileSystemObject" = None):
        """
        Initializes a filesystem object.

        Args:
            name (str): Name of the object (must not be empty).
            parent (Directory, optional): Parent directory. Defaults to None.

        Raises:
            ValueError: If name is empty or consists only of whitespace.
        """
        if not name or not name.strip():
            raise ValueError("Name cannot be empty or whitespace-only")
        self.name = name
        self.parent = parent

    def get_absolute_path(self) -> str:
        """
        Returns the absolute path of this object from the filesystem root.

        Path format follows Unix-style: starts with '/', components separated by '/'.

        Examples:
            - Root: "/"
            - Child of root: "/home"
            - Nested: "/home/user/file.txt"

        Returns:
            str: Absolute path starting with '/'.
        """
        if self.parent is None:
            # Special case: if this is the root, return "/"
            # (Assumes root object has name "/")
            return f"/{self.name}" if self.name != "/" else "/"
        else:
            parent_path = self.parent.get_absolute_path()
            # Avoid double slashes: if parent is root ("/"), don't add extra "/"
            if parent_path == "/":
                return f"/{self.name}"
            return f"{parent_path}/{self.name}"

    def rename(self, new_name: str) -> None:
        """
        Renames the object to a new name.

        Does not affect children or parent — only updates this object's name.

        Args:
            new_name (str): New name (must not be empty or whitespace-only).

        Raises:
            ValueError: If new_name is empty or whitespace-only.
        """
        if not new_name or not new_name.strip():
            raise ValueError("New name cannot be empty or whitespace-only")
        self.name = new_name

    def validate_clone(self, new_parent: "FileSystemObject") -> None:
        """
        Validates parameters before cloning this object.

        Ensures:
          - new_parent is not None
          - new_parent is a FileSystemObject (or subclass)
          - new_parent is not the same as current parent (avoids trivial clones)

        Args:
            new_parent (FileSystemObject): Target parent for the clone.

        Raises:
            ValueError: If new_parent is None or same as current parent.
            TypeError: If new_parent is not a FileSystemObject instance.
        """
        if new_parent is None:
            raise ValueError("New parent cannot be None")
        if not isinstance(new_parent, FileSystemObject):
            raise TypeError(
                "New parent must be a FileSystemObject (or subclass)"
            )
        if new_parent is self.parent:
            raise ValueError(
                "New parent cannot be the same as current directory"
            )

    @abstractmethod
    def clone(self, new_parent: "FileSystemObject") -> "FileSystemObject":
        """
        Creates a deep copy of this object and places it under a new parent.

        Must be implemented by subclasses (File and Directory).
        Should recursively clone children for directories.

        Args:
            new_parent (FileSystemObject): The directory where the clone will be placed.

        Returns:
            FileSystemObject: The newly created clone (same type as self).

        Example:
            cloned_file = original_file.clone(new_directory)
        """
        pass
