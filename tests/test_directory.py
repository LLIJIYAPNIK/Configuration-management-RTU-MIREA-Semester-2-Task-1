import pytest
from file_system import *


def test_directory_creation():
    directory = Directory("test_directory")
    assert directory.name == "test_directory"

    directory2 = Directory("test_directory_2", parent=directory)
    assert directory2.parent.name == "test_directory"

    children = [File("test_file") for _ in range(5)]
    directory3 = Directory("test_directory_3", parent=directory2)
    directory3.children = children

    for i in range(5):
        assert directory3.children[i] == children[i]


def test_bad_directory_creation():
    with pytest.raises(TypeError, match="Parent must be a Directory"):
        Directory("test_directory", parent=File("test_directory"))


def test_directory_add_child():
    directory = Directory("test_directory")
    directory.add_child(File("test_file"))

    assert directory.children["test_file"].name == "test_file"

    parent = Directory("parent")
    child = File("child.txt", parent=parent)
    parent.add_child(child)

    assert "child.txt" in parent.children

    if child.parent and child.name in child.parent.children:
        del child.parent.children[child.name]

    assert "child.txt" not in parent.children


def test_bad_directory_add_child():
    with pytest.raises(TypeError, match="Child must be a FileSystemObject"):
        directory = Directory("test_directory")
        bad_child = 123
        directory.add_child(bad_child)

    with pytest.raises(
        FileExistsError,
        match="Child with name 'test_file' already exists in directory 'test_directory'",
    ):
        directory = Directory("test_directory")
        file = File("test_file")
        same_file = File("test_file")
        directory.add_child(file)
        directory.add_child(same_file)


def test_remove_child():
    directory = Directory("test_directory")
    directory.add_child(File("test_file"))
    directory.remove_child("test_file")


def test_bad_remove_child():
    with pytest.raises(ValueError, match="Child name cannot be empty"):
        directory = Directory("test_directory")
        directory.remove_child("")

    with pytest.raises(
        KeyError,
        match="Child with name 'test_file' does not exist in directory 'test_directory'",
    ):
        directory = Directory("test_directory")
        directory.remove_child("test_file")


def test_get_child():
    directory = Directory("test_directory")
    child = File("test_file")
    directory.add_child(child)

    assert directory.get_child("test_file") == child


def test_bad_get_child():
    with pytest.raises(ValueError, match="Child name cannot be empty"):
        directory = Directory("test_directory")
        directory.get_child("")


def test_directory_get_children():
    directory = Directory("test_directory")
    assert directory.get_children() == {}

    children = [File(f"test_file_{i}") for i in range(5)]
    correct_children = {child.name: child for child in children}

    for child in children:
        directory.add_child(child)

    assert directory.get_children() == correct_children


def test_directory_clone_deep_copy():
    original_parent = Directory("original_parent")
    original_dir = Directory("mydir", original_parent)
    file1 = File("file1.txt", "content1")
    file2 = File("file2.txt", "content2")
    subdir = Directory("subdir")
    file_in_subdir = File("secret.txt", "hidden")

    original_dir.add_child(file1)
    original_dir.add_child(file2)
    original_dir.add_child(subdir)
    subdir.add_child(file_in_subdir)

    new_parent = Directory("new_parent")
    cloned_dir = original_dir.clone(new_parent)

    assert cloned_dir.name == original_dir.name

    assert cloned_dir.parent == new_parent

    assert cloned_dir is not original_dir

    assert len(cloned_dir.children) == len(original_dir.children)

    assert "file1.txt" in cloned_dir.children
    assert "file2.txt" in cloned_dir.children

    cloned_file1 = cloned_dir.children["file1.txt"]
    assert cloned_file1.read() == "content1"
    assert cloned_file1 is not file1

    assert "subdir" in cloned_dir.children
    cloned_subdir = cloned_dir.children["subdir"]

    assert cloned_subdir.name == "subdir"
    assert cloned_subdir.parent == cloned_dir
    assert cloned_subdir is not subdir

    assert "secret.txt" in cloned_subdir.children
    cloned_secret = cloned_subdir.children["secret.txt"]
    assert cloned_secret.read() == "hidden"
    assert cloned_secret is not file_in_subdir

    cloned_file1._content = "modified in clone"
    assert file1.read() == "content1"

    cloned_secret._content = "modified secret"
    assert file_in_subdir.read() == "hidden"

    file2._content = "modified in original"
    cloned_file2 = cloned_dir.children["file2.txt"]
    assert cloned_file2.read() == "content2"


def test_bad_parent_clone():
    directory = Directory("test.txt")
    bad_parent = File("bad_parent")

    with pytest.raises(TypeError, match="Parent must be a Directory"):
        directory.clone(bad_parent)


def test_bad_type_parent_clone():
    directory = Directory("test.txt")
    bad_parent_type = 123

    with pytest.raises(
        TypeError, match="New parent must be a FileSystemObject"
    ):
        directory.clone(bad_parent_type)


def test_same_parent_clone():
    parent = Directory("test_dir")
    directory = Directory("test.txt", parent)

    with pytest.raises(
        ValueError, match="New parent cannot be the same as current directory"
    ):
        directory.clone(parent)
