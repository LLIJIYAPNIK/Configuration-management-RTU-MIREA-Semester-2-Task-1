from typing import Optional, Dict

from abstract import FileSystemObject


class Directory(FileSystemObject):
    """
    Represents a directory (folder) in the virtual filesystem.

    Directories are container nodes that can hold other FileSystemObjects —
    both Files and other Directories. They form the hierarchical structure of the filesystem.

    Key Features:
      - Manages child objects via a name → object dictionary.
      - Supports deep cloning (copies self + all children recursively).
      - Implements Pythonic container interface (__getitem__, __iter__, etc.).
      - Enforces type safety and uniqueness of child names.

    Inheritance:
        FileSystemObject → Directory

    Example:
        root = Directory("/")
        home = Directory("home", parent=root)
        root.add_child(home)
        file = File("readme.txt", parent=home)
        home.add_child(file)
    """

    def __init__(self, name: str, parent: Optional["Directory"] = None):
        """
        Initializes a directory.

        Args:
            name (str): Directory name.
            parent (Directory, optional): Parent directory. Defaults to None.
        """

        if parent:
            if not isinstance(parent, Directory):
                raise TypeError("Parent must be a Directory")

        super().__init__(name, parent)
        self.children: Dict[str, FileSystemObject] = {}

    def add_child(self, child: FileSystemObject) -> None:
        """
        Adds a child object to this directory.

        Args:
            child (FileSystemObject): The object to add.

        Raises:
            TypeError: If child is not a FileSystemObject.
            FileExistsError: If a child with the same name already exists.
        """
        if not isinstance(child, FileSystemObject):
            raise TypeError(f"Child must be a FileSystemObject")
        if child.name in self.children:
            raise FileExistsError(
                f"Child with name '{child.name}' already exists in directory '{self.name}'"
            )
        if child.parent and child.name in child.parent.children:
            del child.parent.children[child.name]
        self.children[child.name] = child
        child.parent = self

    def remove_child(self, child_name: str) -> None:
        """
        Removes a child by name.

        Args:
            child_name (str): Name of the child to remove.

        Raises:
            ValueError: If child_name is empty.
            KeyError: If child does not exist.
        """
        if child_name not in self.children:
            raise KeyError(
                f"Child with name '{child_name}' does not exist in directory '{self.name}'"
            )
        del self.children[child_name]

    def get_child(self, child_name: str) -> Optional[FileSystemObject]:
        """
        Retrieves a child by name.

        Args:
            child_name (str): Name of the child.

        Returns:
            FileSystemObject or None: The child object, or None if not found.

        Raises:
            ValueError: If child_name is empty.
        """
        if child_name not in self.children:
            raise KeyError(
                f"Child with name '{child_name}' does not exist in directory '{self.name}'"
            )
        return self.children.get(child_name)

    def get_children(self) -> Dict[str, FileSystemObject]:
        """Returns a dictionary of all children."""
        return self.children

    def clone(self, new_parent: "Directory") -> "Directory":
        """
        Creates a deep copy of this directory and all its contents.
        Validates parameters using `validate_clone()` before proceeding.

        Args:
            new_parent (Directory): Parent for the cloned directory.

        Returns:
            Directory: The cloned directory.

        Raises:
            ValueError: If new_parent is None or self.
            TypeError: If new_parent is not a Directory.

        See Also:
            validate_clone: Performs parameter validation.
        """
        self.validate_clone(new_parent)
        if not isinstance(new_parent, Directory):
            raise TypeError("Parent must be a Directory")

        new_dir = Directory(self.name, new_parent)
        for child in self.children.values():
            new_child = child.clone(new_dir)
            new_dir.add_child(new_child)
        return new_dir

    def __getitem__(self, item: str) -> FileSystemObject:
        if self.get_child(item):
            return self.children[item]

    def __setitem__(self, key: str, value: FileSystemObject) -> None:
        if self.get_child(key):
            self.children[key] = value

    def __delitem__(self, key: str) -> None:
        if self.get_child(key):
            del self.children[key]

    def __iter__(self):
        return iter(self.children.values())

    def __contains__(self, item: str) -> bool:
        return item in self.children

    def __len__(self) -> int:
        return len(self.children)
