import os
from xml_parser import XmlClient


XML_DATA = """
<filesystem>
    <folder name="home">
        <file name="hello.txt" content="SGVsbG8gV29ybGQh" /> <!-- "Hello World!" -->
        <file name="secret.key" content="c2VjcmV0X2tleV8xMjM=" /> <!-- "secret_key_123" -->
        <folder name="docs">
            <file name="readme.md" content="IyBSZWFkbWUKClRoaXMgaXMgYSB0ZXN0IGZpbGUu" /> <!-- "# Readme\n\nThis is a test file." -->
            <folder name="images">
                <file name="logo.png" content="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJcVd7wbgAAAABJRU5ErkJggg==" />
            </folder>
        </folder>
        <folder name="projects">
            <folder name="project_alpha">
                <file name="main.py" content="cHJpbnQoIkhlbGxvLCBwcm9qZWN0IEFscGhhISIp" /> <!-- print("Hello, project Alpha!") -->
                <file name="config.json" content="eyJzZXR0aW5nIjogInRydWV9" /> <!-- {"setting": "true} -->
            </folder>
            <folder name="project_beta">
                <file name="index.html" content="PGgxPkhlbGxvIEJldGEhPC9oMT4=" /> <!-- <h1>Hello Beta!</h1> -->
            </folder>
        </folder>
    </folder>
    <folder name="tmp">
        <file name="temp.log" content="VGVtcG9yYXJ5IGxvZyBkYXRh" /> <!-- "Temporary log data" -->
    </folder>
    <file name="LICENSE" content="TGljZW5zZWQgdW5kZXIgTUlUIExpY2Vuc2U=" /> <!-- "Licensed under MIT License" -->
</filesystem>
"""

XML_DICT = {
    "/": {
        "home": {
            "hello.txt": "Hello World!",
            "secret.key": "secret_key_123",
            "docs": {
                "readme.md": "# Readme\n\nThis is a test file.",
                "images": {
                    "logo.png": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJcVd7wbgAAAABJRU5ErkJggg=="
                },
            },
            "projects": {
                "project_alpha": {
                    "main.py": 'print("Hello, project Alpha!")',
                    "config.json": '{"setting": "true}',
                },
                "project_beta": {"index.html": "<h1>Hello Beta!</h1>"},
            },
        },
        "tmp": {"temp.log": "Temporary log data"},
        "LICENSE": "Licensed under MIT License",
    }
}

file_path = os.path.join("tests", "test.xml")
with open(file_path, "w") as file:
    for line in XML_DATA:
        file.write(line)
test_xml = XmlClient(file_path)


def test_xml_parser_creation():
    file_path = os.path.join("tests", "test.xml")

    with open(file_path, "w") as file:
        for line in XML_DATA:
            file.write(line)
    test_xml = XmlClient(file_path)

    assert file_path == test_xml.path_to_file
    assert test_xml.xml_obj.tag == "filesystem"
    assert test_xml.xml_dict == XML_DICT

    os.remove(file_path)


def test_xml_get_xml_root():
    file_path = os.path.join("tests", "test.xml")

    with open(file_path, "w") as file:
        for line in XML_DATA:
            file.write(line)
    test_xml = XmlClient(file_path)

    assert test_xml.get_xml_root().tag == "filesystem"

    os.remove(file_path)
