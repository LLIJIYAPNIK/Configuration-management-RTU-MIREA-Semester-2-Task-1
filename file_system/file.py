from base import FileSystemObject


class File(FileSystemObject):
    """Represents a file in the virtual filesystem."""

    def __init__(self, name: str, content: str = "", parent: FileSystemObject = None):
        """
        Initializes a file.

        Args:
            name (str): File name.
            content (str): File content (decoded from base64). Defaults to empty string.
            parent (Directory, optional): Parent directory. Defaults to None.
        """

        if parent:
            if isinstance(parent, File):
                raise TypeError("Parent must be a Directory")
            if parent.name == name:
                raise ValueError("Directory cannot be its own parent")

        super().__init__(name, parent)
        self._content = content

    def read(self) -> str:
        """Returns the file content."""
        return self._content

    def write(self, content: str) -> None:
        """
        Writes new content to the file.

        Args:
            content (str): New content.

        Raises:
            ValueError: If content is empty (use clear() instead).
        """
        if not content:
            raise ValueError("Content cannot be empty; use clear() to clear content")
        self._content = content

    def clear(self) -> None:
        """Clears the file content."""
        self._content = ""

    def clone(self, new_parent: FileSystemObject) -> 'File':
        """
        Creates a copy of this file under a new parent.

        Args:
            new_parent (Directory): Parent for the cloned file.

        Returns:
            File: The cloned file.

        Raises:
            ValueError: If new_parent is None or self.
            TypeError: If new_parent is not a Directory.

        See Also:
            validate_clone: Performs parameter validation.
        """
        self.validate_clone(new_parent)
        if isinstance(new_parent, File):
            raise TypeError("Parent must be a Directory")

        return File(self.name, self._content, new_parent)
