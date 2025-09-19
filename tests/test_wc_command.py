import pytest
from file_system.file_system import FileSystem
from xml_parser import XmlClient
from commands.wc import WcCommand
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
def wc_command_with_vfs(vfs_fs):
    user = User("test", "host")
    env = Environment()
    register = Register(vfs_fs, user, env)

    cmd = WcCommand()
    cmd.register = register
    cmd.register_args()
    return cmd


def test_wc_command_no_flags(capsys, wc_command_with_vfs):
    wc_command_with_vfs.execute(["/home/hello.txt"])

    captured = capsys.readouterr()
    assert captured.out.strip() == "1 2 12 hello.txt"


def test_wc_command_flag_I(capsys, wc_command_with_vfs):
    wc_command_with_vfs.execute(["-I", "/home/hello.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "1 hello.txt"


def test_wc_command_flag_w(capsys, wc_command_with_vfs):
    wc_command_with_vfs.execute(["-w", "/home/hello.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "2 hello.txt"


def test_wc_command_flag_m(capsys, wc_command_with_vfs):
    wc_command_with_vfs.execute(["-m", "/home/hello.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "12 hello.txt"


def test_wc_command_flag_L(capsys, wc_command_with_vfs):
    content = "Short\nLonger line\nLongest line in file"
    from file_system.file import File

    tmp_folder = wc_command_with_vfs.register.fs.find("/tmp")
    test_file = File("test.txt", content)
    tmp_folder.add_child(test_file)

    wc_command_with_vfs.execute(["-L", "/tmp/test.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "20 test.txt"


def test_wc_command_multiple_flags(capsys, wc_command_with_vfs):
    content = "Line 1\nLine 22\nLine 333"
    from file_system.file import File

    tmp_folder = wc_command_with_vfs.register.fs.find("/tmp")
    test_file = File("test.txt", content)
    tmp_folder.add_child(test_file)

    wc_command_with_vfs.execute(["-w", "-I", "-L", "/tmp/test.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "6 3 8 test.txt"


def test_wc_command_file_not_exists(wc_command_with_vfs):
    with pytest.raises(
        FileExistsError, match="File does not exists. Check your path."
    ):
        wc_command_with_vfs.execute(["/nonexistent.txt"])


def test_wc_command_empty_file(capsys, wc_command_with_vfs, vfs_fs):
    from file_system.file import File

    tmp_folder = vfs_fs.find("/tmp")
    empty_file = File("empty.txt", "")
    tmp_folder.add_child(empty_file)

    wc_command_with_vfs.execute(["/tmp/empty.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "1 0 0 empty.txt"

    wc_command_with_vfs.execute(["-w", "/tmp/empty.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "0 empty.txt"

    wc_command_with_vfs.execute(["-m", "/tmp/empty.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "0 empty.txt"

    wc_command_with_vfs.execute(["-L", "/tmp/empty.txt"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "0 empty.txt"
