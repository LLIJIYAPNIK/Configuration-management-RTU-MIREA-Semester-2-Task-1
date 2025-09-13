import base64
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict


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