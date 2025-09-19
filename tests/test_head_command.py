import pytest
from file_system.file_system import FileSystem
from xml_parser import XmlClient
from commands.head import HeadCommand
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
def head_command_with_vfs(vfs_fs):
    user = User("test", "host")
    env = Environment()
    register = Register(vfs_fs, user, env)

    cmd = HeadCommand()
    cmd.register = register
    cmd.register_args()
    return cmd


def test_head_command_default_10_rows(capsys, head_command_with_vfs):
    content = "Line 1\nLine 2\nLine 3"
    from file_system.file import File

    tmp_folder = head_command_with_vfs.register.fs.find("/tmp")
    test_file = File("test.txt", content)
    tmp_folder.add_child(test_file)

    head_command_with_vfs.execute(["/tmp/test.txt"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0] == "test.txt"
    assert lines[1:] == ["Line 1", "Line 2", "Line 3"]


def test_head_command_with_n_flag(capsys, head_command_with_vfs):
    content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
    from file_system.file import File

    tmp_folder = head_command_with_vfs.register.fs.find("/tmp")
    test_file = File("test.txt", content)
    tmp_folder.add_child(test_file)

    head_command_with_vfs.execute(["-n", "3", "/tmp/test.txt"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0] == "test.txt"
    assert lines[1:] == ["Line 1", "Line 2", "Line 3"]


def test_head_command_file_not_exists(head_command_with_vfs):
    with pytest.raises(
        FileExistsError, match="File does not exists. Check your path."
    ):
        head_command_with_vfs.execute(["/nonexistent.txt"])


def test_head_command_n_less_than_1(head_command_with_vfs):
    """-n <= 0 — ошибка."""
    with pytest.raises(
        ValueError, match="Number have to be more than 0. Your n: 0"
    ):
        head_command_with_vfs.execute(["-n", "0", "/LICENSE"])

    with pytest.raises(
        ValueError, match="Number have to be more than 0. Your n: -5"
    ):
        head_command_with_vfs.execute(["-n", "-5", "/LICENSE"])


def test_head_command_multiple_paths_uses_first(capsys, head_command_with_vfs):
    head_command_with_vfs.execute(["/home/hello.txt", "/home/docs/readme.md"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0] == "hello.txt"
    assert lines[1] == "Hello World!"


def test_head_command_empty_file(capsys, head_command_with_vfs, vfs_fs):
    from file_system.file import File

    tmp_folder = vfs_fs.find("/tmp")
    empty_file = File("empty.txt", "")
    tmp_folder.add_child(empty_file)

    head_command_with_vfs.execute(["/tmp/empty.txt"])

    captured = capsys.readouterr()
    lines = captured.out.split("\n")

    assert lines[0] == "empty.txt"
    assert lines[1] == ""
    assert len(lines) >= 2


def test_head_command_single_line(capsys, head_command_with_vfs):
    head_command_with_vfs.execute(["/home/hello.txt"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0] == "hello.txt"
    assert lines[1] == "Hello World!"
