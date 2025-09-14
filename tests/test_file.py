import pytest
from file_system import *


def test_file_creation():
    f = File("test.txt", "Hello World")
    assert f.name == "test.txt"
    assert f.read() == "Hello World"


def test_bad_file_creation():
    bad_parent = File("bad_parent", "Hello World")

    with pytest.raises(TypeError, match="Parent must be a Directory"):
        File("test.txt", "Hello World", bad_parent)


def test_file_read():
    f = File("test.txt", "Hello World")
    assert f.read() == "Hello World"


def test_file_write():
    f = File("test.txt", "Hello World")
    f.write("Goodbye World")
    assert f.read() == "Goodbye World"


def test_bad_file_write():
    f = File("test.txt", "Hello World")
    with pytest.raises(
        ValueError,
        match=r"Content cannot be empty; use clear\(\) to clear content",
    ):
        f.write("")


def test_file_clear():
    f = File("test.txt", "Hello World")
    f.clear()
    assert f.read() == ""


def test_clone():
    f = File("test.txt", "Hello World")
    directory = Directory("test_dir")

    new_f = f.clone(directory)
    assert f.name == new_f.name
    assert f.read() == new_f.read()
    assert new_f.parent == directory


def test_bad_parent_clone():
    f = File("test.txt", "Hello World")
    bad_parent = File("bad_parent")

    with pytest.raises(TypeError, match="Parent must be a Directory"):
        f.clone(bad_parent)


def test_bad_type_parent_clone():
    f = File("test.txt", "Hello World")
    bad_parent_type = 123

    with pytest.raises(
        TypeError, match="New parent must be a FileSystemObject"
    ):
        f.clone(bad_parent_type)


def test_same_parent_clone():
    directory = Directory("test_dir")
    f = File("test.txt", "Hello World", directory)

    with pytest.raises(
        ValueError, match="New parent cannot be the same as current directory"
    ):
        f.clone(directory)
