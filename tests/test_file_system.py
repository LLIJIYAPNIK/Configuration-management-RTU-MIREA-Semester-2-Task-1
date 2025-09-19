import pytest

from file_system import Directory
from file_system.file_system import FileSystem

TEST_TREE = {
    "/": {
        "home": {"file1.txt": "Hello", "docs": {"readme.md": "# Readme"}},
        "tmp": {},
        "LICENSE": "MIT",
    }
}


def test_filesystem_creation():
    fs = FileSystem(TEST_TREE)
    assert fs.root.name == "/"
    assert fs.cwd == fs.root


def test_bad_file_system_creation():
    with pytest.raises(
        ValueError,
        match=r"Root directory \('/'\) not found in tree_dict",
    ):
        fs = FileSystem({})
        fs.create_file_system()


def test_create_file_system():
    """Тестирует построение дерева из словаря."""
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    home = fs.find("/home")
    assert home is not None
    assert home.name == "home"

    file1 = fs.find("/home/file1.txt")
    assert file1 is not None
    assert file1.read() == "Hello"

    readme = fs.find("/home/docs/readme.md")
    assert readme is not None
    assert readme.read() == "# Readme"

    license_file = fs.find("/LICENSE")
    assert license_file is not None
    assert license_file.read() == "MIT"


def test_cd_and_pwd():
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    fs.cd("/home")
    assert fs.pwd == "/home"

    fs.cd("docs")
    assert fs.pwd == "/home/docs"

    fs.cd("..")
    assert fs.pwd == "/home"

    fs.cd("/")
    assert fs.pwd == "/"


def test_bad_cd():
    with pytest.raises(ValueError, match="Already at root directory"):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.cd("..")
    with pytest.raises(
        NotADirectoryError, match="Path '/LICENSE' is not a directory"
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.cd("/LICENSE")
    with pytest.raises(
        FileNotFoundError, match="Directory '/no/this/path' not found"
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.cd("/no/this/path")


def test_ls():
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    fs.cd("/home")
    contents = fs.ls()
    assert set(contents) == {"file1.txt", "docs"}

    fs.cd("docs")
    contents = fs.ls()
    assert contents == ["readme.md"]


def test_bad_ls():
    with pytest.raises(NotADirectoryError, match="Path is a file"):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.ls("/LICENSE")


def test_mkdir_and_touch():
    fs = FileSystem({"": {}})
    fs.root = Directory("/")
    fs.cwd = fs.root

    fs.mkdir("newdir")
    assert fs.exists("/newdir")

    fs.touch("newfile.txt")
    assert fs.exists("/newfile.txt")

    with pytest.raises(FileExistsError):
        fs.mkdir("newdir")

    with pytest.raises(FileExistsError):
        fs.touch("newfile.txt")


def test_resolve_parent_and_name():
    with pytest.raises(ValueError, match="Path cannot be empty"):
        fs = FileSystem(TEST_TREE)
        fs.resolve_parent_and_name("")
    with pytest.raises(
        FileNotFoundError, match="Parent directory not found: no/path"
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.resolve_parent_and_name("no/path/file.txt")
    with pytest.raises(
        NotADirectoryError,
        match="Path 'home/docs/readme.md' is not a directory",
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.resolve_parent_and_name("home/docs/readme.md/nothing")


def test_rm():
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    fs.rm("/home/file1.txt")
    assert not fs.exists("/home/file1.txt")

    fs.rm("/home/docs")
    assert not fs.exists("/home/docs")


def test_validate_move_or_copy():
    with pytest.raises(ValueError, match="Source path cannot be empty"):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.validate_move_or_copy("", "/home")
    with pytest.raises(ValueError, match="Destination path cannot be empty"):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.validate_move_or_copy("/home", "")
    with pytest.raises(
        ValueError, match="Source and destination paths must differ"
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.validate_move_or_copy("/home", "/home")
    with pytest.raises(FileNotFoundError, match="Object '/no/path' not found"):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.validate_move_or_copy("/no/path", "/home")
    with pytest.raises(FileNotFoundError, match="Object '/no/path' not found"):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.validate_move_or_copy("/home", "/no/path")
    with pytest.raises(
        NotADirectoryError,
        match="Destination path '/home/docs/readme.md' is not a directory",
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.validate_move_or_copy("/home", "/home/docs/readme.md")
    with pytest.raises(
        FileExistsError,
        match="Object 'LICENSE' already exists in '/home/docs'",
    ):
        fs = FileSystem(TEST_TREE)
        fs.create_file_system()
        fs.touch("/home/docs/LICENSE")
        fs.validate_move_or_copy("/LICENSE", "/home/docs/")


def test_move():
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    fs.move("/home/file1.txt", "/tmp")
    assert not fs.exists("/home/file1.txt")
    assert fs.exists("/tmp/file1.txt")


def test_copy():
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    tmp_dir = fs.find("/tmp")
    assert tmp_dir is not None
    assert tmp_dir.parent is not None, "Directory '/tmp' has no parent!"

    fs.copy("/home/file1.txt", "/tmp")
    assert fs.exists("/home/file1.txt")


def test_find_and_exists():
    fs = FileSystem(TEST_TREE)
    fs.create_file_system()

    assert fs.find("/home") is not None
    assert fs.find("/nonexistent") is None

    assert fs.exists("/home")
    assert not fs.exists("/nonexistent")
