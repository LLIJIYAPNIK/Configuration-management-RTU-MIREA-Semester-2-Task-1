import pytest
from io import StringIO
import xml.etree.ElementTree as ET
from unittest.mock import Mock
from file_system.file_system import FileSystem
from xml_parser import XmlClient
from commands.tac import TacCommand
from user import User
from environment import Environment
from commands.register import Register


XML_STR = """
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


@pytest.fixture(scope="session")
def xml_dict():
    return XmlClient(xml_str=XML_STR).xml_dict


@pytest.fixture
def vfs_fs(xml_dict):
    fs = FileSystem(xml_dict)
    fs.create_file_system()
    return fs


@pytest.fixture
def tac_command_with_vfs(vfs_fs):
    user = User("test", "host")
    env = Environment()
    register = Register(vfs_fs, user, env)

    cmd = TacCommand()
    cmd.register = register
    cmd.register_args()
    return cmd


def test_tac_command_hello_txt(capsys, tac_command_with_vfs):
    tac_command_with_vfs.execute(["/home/hello.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello World!"


def test_tac_command_readme_md(capsys, tac_command_with_vfs):
    tac_command_with_vfs.execute(["/home/docs/readme.md"])
    captured = capsys.readouterr()

    expected = "This is a test file.\n\n# Readme"
    assert captured.out.strip() == expected


def test_tac_command_main_py(capsys, tac_command_with_vfs):
    tac_command_with_vfs.execute(["/home/projects/project_alpha/main.py"])
    captured = capsys.readouterr()
    assert captured.out.strip() == 'print("Hello, project Alpha!")'


def test_tac_command_license(capsys, tac_command_with_vfs):
    tac_command_with_vfs.execute(["/LICENSE"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "Licensed under MIT License"


def test_tac_command_file_not_exists(tac_command_with_vfs):
    with pytest.raises(
        FileExistsError, match="File does not exists. Check your path."
    ):
        tac_command_with_vfs.execute(["/nonexistent.txt"])


def test_tac_command_uses_first_path(capsys, tac_command_with_vfs):
    tac_command_with_vfs.execute(["/home/hello.txt", "/home/docs/readme.md"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello World!"


def test_tac_command_empty_file(capsys, tac_command_with_vfs, vfs_fs):
    from file_system.file import (
        File,
    )

    tmp_folder = vfs_fs.find("/tmp")
    empty_file = File("empty.txt", "")
    tmp_folder.add_child(empty_file)

    tac_command_with_vfs.execute(["/tmp/empty.txt"])
    captured = capsys.readouterr()
    assert captured.out == "\n"
