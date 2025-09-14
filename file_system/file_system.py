import base64
from typing import Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET

from file_system.directory import Directory
from file_system.file import File


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

    def _build_tree(
        self, parent_dir: Directory, structure: Dict[str, Any]
    ) -> None:
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

    def _print_directory_tree(
        self, directory: Directory, indent: int, level: int
    ) -> None:
        """
        Recursively prints a directory and its contents.

        Args:
            directory (Directory): Directory to print.
            indent (int): Spaces per level.
            level (int): Current depth level.
        """
        prefix = " " * (indent * level)
        (
            print(f"{prefix}{directory.name}/")
            if directory.name != "/"
            else print("/")
        )

        children_sorted = sorted(
            directory.children.values(),
            key=lambda obj: (not isinstance(obj, Directory), obj.name),
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

    def ls(self, path: str = None) -> list[str] | None:
        if path is None or path == ".":
            return [_.name for _ in self.cwd]
        else:
            obj = self.find(path)
            if obj is None:
                return None
            if isinstance(obj, Directory):
                return [_.name for _ in obj]
            if isinstance(obj, File):
                raise NotADirectoryError("Path is a file")
            return None

    def find(
        self, path: str, temp_cwd: Optional[Directory] = None
    ) -> Directory | File | None:
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
                raise FileNotFoundError(
                    f"Parent directory not found: {parent_path}"
                )
            if not isinstance(parent, Directory):
                raise NotADirectoryError(
                    f"Path '{parent_path}' is not a directory"
                )

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
            raise FileExistsError(
                f"Object '{name}' already exists in '{parent.get_absolute_path()}'"
            )
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
            raise FileExistsError(
                f"Object '{name}' already exists in '{parent.get_absolute_path()}'"
            )
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
            raise FileNotFoundError(
                f"Object '{name}' not found in '{parent.get_absolute_path()}'"
            )
        del parent.children[name]

    def validate_move_or_copy(
        self, from_path: str, to_path: str
    ) -> Tuple[Directory | File | None, Directory]:
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
            raise NotADirectoryError(
                f"Destination path '{to_path}' is not a directory"
            )

        if from_obj.name in to_obj:
            raise FileExistsError(
                f"Object '{from_obj.name}' already exists in '{to_obj.get_absolute_path()}'"
            )

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

    def to_xml_element(self) -> ET.Element:
        """
        Converts the file system into an XML element with <filesystem> as root.

        Returns:
            xml.etree.ElementTree.Element: The root XML element representing the entire file system.
        """
        filesystem_elem = ET.Element("filesystem")
        self._add_children_to_xml(filesystem_elem, self.root)
        return filesystem_elem

    def _add_children_to_xml(
        self, parent_xml_elem: ET.Element, dir_obj: Directory
    ) -> None:
        """
        Recursively adds children of a directory to the given XML element.

        Args:
            parent_xml_elem (xml.etree.ElementTree.Element): The parent XML element to append children to.
            dir_obj (Directory): The directory object whose children should be serialized.
        """
        for name, obj in dir_obj.children.items():
            if isinstance(obj, File):
                file_elem = ET.Element("file")
                file_elem.set("name", name)
                encoded_content = base64.b64encode(
                    obj.read().encode("utf-8")
                ).decode("utf-8")
                file_elem.set("content", encoded_content)
                parent_xml_elem.append(file_elem)

            elif isinstance(obj, Directory):
                folder_elem = ET.Element("folder")
                folder_elem.set("name", name)
                parent_xml_elem.append(folder_elem)
                self._add_children_to_xml(folder_elem, obj)

    def save_to_xml(self, filepath: str) -> None:
        """
        Saves the current file system state to an XML file.

        Serializes the entire file system into XML format and writes it to the specified file path.
        The output is UTF-8 encoded with an XML declaration and pretty-printed indentation.

        Args:
            filepath (str): The path where the XML file will be saved.
        """
        root_elem = self.to_xml_element()
        tree = ET.ElementTree(root_elem)
        ET.indent(tree, space="    ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
