from abstract import FileSystemObject


class File(FileSystemObject):
    """
    Represents a file (leaf node) in the virtual filesystem.

    Files store textual or binary content (typically decoded from base64 in XML source).
    Unlike directories, files cannot have children — they are terminal nodes in the filesystem tree.

    Key Features:
      - Stores content as a string (supports any text or base64-decoded binary data).
      - Provides safe write/clear operations.
      - Supports cloning (shallow copy of content and metadata).
      - Enforces that parent must be a Directory (not another File).

    Inheritance:
        FileSystemObject → File

    Example:
        parent_dir = Directory("docs")
        readme = File("readme.txt", "Hello, World!", parent=parent_dir)
        print(readme.read())  # → "Hello, World!"
    """

    def __init__(
        self, name: str, content: str = "", parent: FileSystemObject = None
    ):
        """
        Initializes a file with optional content and parent directory.

        Args:
            name (str): File name (must not be empty — validated by parent class).
            content (str): Initial file content. Typically decoded from base64.
                           Defaults to empty string.
            parent (Directory, optional): Parent directory. Must be a Directory instance.
                                          Defaults to None.

        Raises:
            TypeError: If parent is provided and is a File (not a Directory).
            ValueError: If name is empty (raised by FileSystemObject.__init__).
        """
        if parent is not None:
            if isinstance(parent, File):
                raise TypeError("Parent must be a Directory, not a File")
            if not isinstance(parent, FileSystemObject):
                raise TypeError("Parent must be a FileSystemObject")

        super().__init__(name, parent)
        self._content = content

    def read(self) -> str:
        """
        Returns the current content of the file.

        Returns:
            str: File content as a string. May be empty.
        """
        return self._content

    def write(self, content: str) -> None:
        """
        Overwrites the file's content with new content.

        Prevents accidental empty writes — use `clear()` for intentional clearing.

        Args:
            content (str): New content to write. Must not be empty.

        Raises:
            ValueError: If content is empty or None. Use `clear()` instead.
        """
        if not content:
            raise ValueError(
                "Content cannot be empty; use clear() to clear content"
            )
        self._content = content

    def clear(self) -> None:
        """
        Empties the file content.

        Sets content to empty string — safe and explicit way to clear a file.
        """
        self._content = ""

    def clone(self, new_parent: FileSystemObject) -> "File":
        """
        Creates a shallow copy of this file under a new parent directory.

        Cloning preserves:
          - File name
          - File content
          - Does NOT preserve parent (new_parent is assigned)

        Uses `validate_clone()` for input validation.

        Args:
            new_parent (Directory): The directory where the cloned file will be placed.

        Returns:
            File: A new File instance with same name and content.

        Raises:
            ValueError: If new_parent is None or same as current parent.
            TypeError: If new_parent is not a Directory (or is a File).

        See Also:
            validate_clone: Performs parameter validation (inherited from FileSystemObject).
        """
        self.validate_clone(new_parent)

        if isinstance(new_parent, File):
            raise TypeError("Parent must be a Directory, not a File")
        if not isinstance(new_parent, FileSystemObject):
            raise TypeError("Parent must be a FileSystemObject")

        return File(self.name, self._content, new_parent)
