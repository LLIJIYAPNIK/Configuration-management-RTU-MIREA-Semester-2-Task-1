import xml.etree.ElementTree as ET
import base64
from pathlib import Path


class XmlClient:
    def __init__(self, path_to_file: str):
        self.path_to_file = path_to_file
        self.xml_obj = self.get_xml_root(self.path_to_file)
        self.xml_dict = {"/": self.xml_to_dict(self.xml_obj, is_root=True)}

    @staticmethod
    def get_xml_root(path_to_file: str) -> ET.Element:
        tree = ET.parse(path_to_file)
        return tree.getroot()

    def xml_to_dict(self, xml_input, is_root=True):
        if isinstance(xml_input, (str, Path)):
            tree = ET.parse(xml_input)
            root = tree.getroot()
            return self.xml_to_dict(root, is_root=True)

        if not isinstance(xml_input, ET.Element):
            raise TypeError("xml_input must to be a string, Path or Element")

        element = xml_input

        if is_root:
            result = {}
            for child in element:
                name = child.get("name")
                if not name:
                    continue
                result[name] = self.xml_to_dict(child, is_root=False)
            return result

        if element.tag == "folder":
            content = {}
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

print(XmlClient("test_vfs.xml").xml_dict)
