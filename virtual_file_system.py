import xml.etree.ElementTree as ET
import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class XmlClient:
    """Parses XML file representing a virtual filesystem and converts it to a nested dictionary."""

    def __init__(self, path_to_file: str):
        """
        Initializes XmlClient by parsing the given XML file.

        Args:
            path_to_file (str): Path to the XML file.
        """
        self.path_to_file = path_to_file
        self.xml_obj = self.get_xml_root(self.path_to_file)
        self.xml_dict = {"/": self.xml_to_dict(self.xml_obj, is_root=True)}

    @staticmethod
    def get_xml_root(path_to_file: str) -> ET.Element:
        """
        Parses XML file and returns the root element.

        Args:
            path_to_file (str): Path to the XML file.

        Returns:
            xml.etree.ElementTree.Element: Root element of the XML tree.

        Raises:
            FileNotFoundError: If the file does not exist.
            ET.ParseError: If the XML is malformed.
        """
        tree = ET.parse(path_to_file)
        return tree.getroot()

    def xml_to_dict(self, xml_input: Any, is_root: bool = True) -> Any:
        """
        Recursively converts XML structure into a nested dictionary.
        Folders become dictionaries, files become decoded strings (from base64).

        Args:
            xml_input: Can be a file path (str/Path) or an XML Element.
            is_root (bool): Whether the current element is the filesystem root.

        Returns:
            Any: Dictionary for folders, string for files, None otherwise.

        Raises:
            TypeError: If xml_input is not a supported type.
        """
        if isinstance(xml_input, (str, Path)):
            tree = ET.parse(xml_input)
            root = tree.getroot()
            return self.xml_to_dict(root, is_root=True)

        if not isinstance(xml_input, ET.Element):
            raise TypeError("xml_input must be a string, Path, or Element")

        element = xml_input

        if is_root:
            result: Dict[str, Any] = {}
            for child in element:
                name = child.get("name")
                if not name:
                    continue
                result[name] = self.xml_to_dict(child, is_root=False)
            return result

        if element.tag == "folder":
            content: Dict[str, Any] = {}
            for child in element:
                name = child.get("name")
                if not name:
                    continue
                content[name] = self.xml_to_dict(child, is_root=False)
            return content

        elif element.tag == "file":
            content_b64 = element.get("content", "")
            try:
                decoded = base64.b64decode(content_b64).decode('utf-8')
            except Exception:
                decoded = content_b64
            return decoded

        return None


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


class Directory(FileSystemObject):
    """Represents a directory in the virtual filesystem."""

    def __init__(self, name: str, parent: Optional['Directory'] = None):
        """
        Initializes a directory.

        Args:
            name (str): Directory name.
            parent (Directory, optional): Parent directory. Defaults to None.
        """
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
            raise TypeError("Child must be a FileSystemObject")
        if child.name in self.children:
            raise FileExistsError(f"Child with name '{child.name}' already exists in directory '{self.name}'")
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
        if not child_name:
            raise ValueError("Child name cannot be empty")
        if child_name not in self.children:
            raise KeyError(f"Child with name '{child_name}' does not exist in directory '{self.name}'")
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
        if not child_name:
            raise ValueError("Child name cannot be empty")
        return self.children.get(child_name)

    def get_children(self) -> Dict[str, FileSystemObject]:
        """Returns a dictionary of all children."""
        return self.children

    def clone(self, new_parent: 'Directory') -> 'Directory':
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
        new_dir = Directory(self.name, new_parent)
        for child in self.children.values():
            new_child = child.clone(new_dir)
            new_dir.add_child(new_child)
        return new_dir

    def __getitem__(self, item: str) -> FileSystemObject:
        if not item:
            raise ValueError("Child name cannot be empty")
        return self.children[item]

    def __setitem__(self, key: str, value: FileSystemObject) -> None:
        if not key:
            raise ValueError("Key (child name) cannot be empty")
        if not value:
            raise ValueError("Value (child object) cannot be empty")
        if not isinstance(value, FileSystemObject):
            raise ValueError("Value must be a FileSystemObject")
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        self.children[key] = value
        value.parent = self

    def __delitem__(self, key: str) -> None:
        if not key:
            raise ValueError("Child name cannot be empty")
        del self.children[key]

    def __iter__(self):
        return iter(self.children.values())

    def __contains__(self, item: str) -> bool:
        if not isinstance(item, str):
            raise TypeError("Item must be a string")
        if not item:
            raise ValueError("Item cannot be empty")
        return item in self.children

    def __len__(self) -> int:
        return len(self.children)


class File(FileSystemObject):
    """Represents a file in the virtual filesystem."""

    def __init__(self, name: str, content: str = "", parent: Optional[Directory] = None):
        """
        Initializes a file.

        Args:
            name (str): File name.
            content (str): File content (decoded from base64). Defaults to empty string.
            parent (Directory, optional): Parent directory. Defaults to None.
        """
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

    def clone(self, new_parent: 'Directory') -> 'File':
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
        return File(self.name, self._content, new_parent)


class FileSystem:
    """Manages a virtual filesystem built from a dictionary structure."""

    def __init__(self, tree_dict: Dict[str, Any]):
        """
        Initializes the filesystem with a root directory.

        Args:
            tree_dict (dict): Dictionary representation of the filesystem (must contain root key "/").
        """
        self.root = Directory("/")
        self.cwd = self.root
        self.tree_dict = tree_dict

    def create_file_system(self) -> None:
        """
        Builds the object-based filesystem from the dictionary structure.

        Raises:
            ValueError: If root key "/" is missing in tree_dict.
        """
        if "/" not in self.tree_dict:
            raise ValueError("Root directory ('/') not found in tree_dict")
        self._build_tree(self.root, self.tree_dict["/"])

    def _build_tree(self, parent_dir: Directory, structure: Dict[str, Any]) -> None:
        """
        Recursively builds the filesystem tree from a dictionary.

        Args:
            parent_dir (Directory): Parent directory to attach children to.
            structure (dict): Dictionary representing current level of the tree.
        """
        for name, content in structure.items():
            if isinstance(content, dict):
                new_dir = Directory(name)
                parent_dir.add_child(new_dir)
                self._build_tree(new_dir, content)
            else:
                new_file = File(name, content=str(content) if content else "")
                parent_dir.add_child(new_file)

    def print_tree(self, path: str = "/", indent: int = 2) -> None:
        """
        Prints the filesystem tree starting from the specified path.

        Args:
            path (str): Starting directory path. Defaults to root "/".
            indent (int): Number of spaces per indentation level. Defaults to 2.

        Output:
            Prints tree to stdout.
        """
        obj = self.find(path)
        if obj is None:
            print(f"Error: Path '{path}' not found.")
            return

        if not isinstance(obj, Directory):
            print(f"Error: '{path}' is not a directory.")
            return

        self._print_directory_tree(obj, indent=indent, level=0)

    def _print_directory_tree(self, directory: Directory, indent: int, level: int) -> None:
        """
        Recursively prints a directory and its contents.

        Args:
            directory (Directory): Directory to print.
            indent (int): Spaces per level.
            level (int): Current depth level.
        """
        prefix = " " * (indent * level)
        print(f"{prefix}{directory.name}/") if directory.name != "/" else print("/")

        children_sorted = sorted(
            directory.children.values(),
            key=lambda obj: (not isinstance(obj, Directory), obj.name)
        )

        for child in children_sorted:
            child_prefix = " " * (indent * (level + 1))
            if isinstance(child, Directory):
                self._print_directory_tree(child, indent, level + 1)
            else:
                print(f"{child_prefix}{child.name}")

    @property
    def pwd(self) -> str:
        """Returns the absolute path of the current working directory."""
        return self.cwd.get_absolute_path()

    def cd(self, path: str) -> None:
        """
        Changes the current working directory.

        Args:
            path (str): Target directory path.

        Raises:
            ValueError: If path is empty or already at root when going up.
            FileNotFoundError: If path does not exist.
            NotADirectoryError: If target is not a directory.
        """
        if not path:
            raise ValueError("Path cannot be empty")

        if path == "..":
            if self.cwd.parent:
                self.cwd = self.cwd.parent
            else:
                raise ValueError("Already at root directory")
        elif path == ".":
            pass
        elif path == "/":
            self.cwd = self.root
        elif self.exists(path):
            target = self.find(path)
            if isinstance(target, Directory):
                self.cwd = target
            else:
                raise NotADirectoryError(f"Path '{path}' is not a directory")
        else:
            raise FileNotFoundError(f"Directory '{path}' not found")

    def find(self, path: str, temp_cwd: Optional[Directory] = None) -> Optional[FileSystemObject]:
        """
        Finds a filesystem object by path.

        Args:
            path (str): Path to the object.
            temp_cwd (Directory, optional): Starting directory. Defaults to root.

        Returns:
            FileSystemObject or None: Found object, or None if not found.
        """
        if temp_cwd is None:
            temp_cwd = self.root

        parts = [p for p in path.split("/") if p]

        if not parts:
            return temp_cwd

        current_part = parts[0]
        if current_part not in temp_cwd:
            return None

        obj = temp_cwd.children[current_part]

        if len(parts) == 1:
            return obj

        if isinstance(obj, Directory):
            return self.find("/".join(parts[1:]), obj)
        else:
            return None

    def exists(self, path: str, temp_cwd: Optional[Directory] = None) -> bool:
        """
        Checks if a path exists.

        Args:
            path (str): Path to check.
            temp_cwd (Directory, optional): Starting directory. Defaults to root.

        Returns:
            bool: True if path exists, False otherwise.
        """
        return self.find(path, temp_cwd) is not None

    def resolve_parent_and_name(self, path: str) -> Tuple[Directory, str]:
        """
        Splits a path into its parent directory and target name.

        Args:
            path (str): Full path.

        Returns:
            tuple: (parent_directory, name)

        Raises:
            ValueError: If path is empty.
            FileNotFoundError: If parent directory does not exist.
            NotADirectoryError: If parent is not a directory.
        """
        parts = [p for p in path.split("/") if p]

        if not parts:
            raise ValueError("Path cannot be empty")

        name = parts[-1]

        if len(parts) == 1:
            parent = self.cwd
        else:
            parent_path = "/".join(parts[:-1])
            parent = self.find(parent_path)
            if parent is None:
                raise FileNotFoundError(f"Parent directory not found: {parent_path}")
            if not isinstance(parent, Directory):
                raise NotADirectoryError(f"Path '{parent_path}' is not a directory")

        return parent, name

    def mkdir(self, path: str) -> None:
        """
        Creates a new directory.

        Args:
            path (str): Path for the new directory.

        Raises:
            ValueError: If path is invalid.
            FileExistsError: If directory already exists.
        """
        parent, name = self.resolve_parent_and_name(path)
        if name in parent:
            raise FileExistsError(f"Object '{name}' already exists in '{parent.get_absolute_path()}'")
        parent.add_child(Directory(name))

    def touch(self, path: str) -> None:
        """
        Creates a new empty file.

        Args:
            path (str): Path for the new file.

        Raises:
            ValueError: If path is invalid.
            FileExistsError: If file already exists.
        """
        parent, name = self.resolve_parent_and_name(path)
        if name in parent:
            raise FileExistsError(f"Object '{name}' already exists in '{parent.get_absolute_path()}'")
        parent.add_child(File(name))

    def rm(self, path: str) -> None:
        """
        Removes a file or directory.

        Args:
            path (str): Path to remove.

        Raises:
            ValueError: If path is invalid.
            FileNotFoundError: If object does not exist.
        """
        parent, name = self.resolve_parent_and_name(path)
        if name not in parent:
            raise FileNotFoundError(f"Object '{name}' not found in '{parent.get_absolute_path()}'")
        del parent.children[name]

    def validate_move_or_copy(self, from_path: str, to_path: str) -> Tuple[FileSystemObject, Directory]:
        """
        Validates paths for move or copy operations.

        Args:
            from_path (str): Source path.
            to_path (str): Destination path.

        Returns:
            tuple: (source_object, target_directory)

        Raises:
            ValueError: If paths are empty or identical.
            FileNotFoundError: If source or target not found.
            NotADirectoryError: If target is not a directory.
            FileExistsError: If destination already contains an object with the same name.
        """
        if not from_path:
            raise ValueError("Source path cannot be empty")
        if not to_path:
            raise ValueError("Destination path cannot be empty")
        if from_path == to_path:
            raise ValueError("Source and destination paths must differ")

        from_obj = self.find(from_path)
        if from_obj is None:
            raise FileNotFoundError(f"Object '{from_path}' not found")

        to_obj = self.find(to_path)
        if to_obj is None:
            raise FileNotFoundError(f"Object '{to_path}' not found")

        if not isinstance(to_obj, Directory):
            raise NotADirectoryError(f"Destination path '{to_path}' is not a directory")

        if from_obj.name in to_obj:
            raise FileExistsError(f"Object '{from_obj.name}' already exists in '{to_obj.get_absolute_path()}'")

        return from_obj, to_obj

    def move(self, from_: str, to: str) -> None:
        """
        Moves a filesystem object to a new directory.

        Args:
            from_ (str): Source path.
            to (str): Destination directory path.

        See also: validate_move_or_copy
        """
        from_obj, to_dir = self.validate_move_or_copy(from_, to)
        to_dir.add_child(from_obj)

    def copy(self, from_: str, to: str) -> None:
        """
        Copies a filesystem object to a new directory.

        Args:
            from_ (str): Source path.
            to (str): Destination directory path.

        See also: validate_move_or_copy
        """
        from_obj, to_dir = self.validate_move_or_copy(from_, to)
        copied_obj = from_obj.clone(to_dir)
        to_dir.add_child(copied_obj)


if __name__ == "__main__":
    dict_tree = XmlClient("test_vfs.xml").xml_dict
    fs = FileSystem(dict_tree)
    fs.create_file_system()
    fs.print_tree()
