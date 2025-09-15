import pytest
from file_system.file_system import FileSystem
from commands import Register, CdCommand


def test_to_register():
    file_system = FileSystem({"/": {}})
    register = Register(file_system)

    register.register("cd", CdCommand)

    assert "cd" in register.commands
    assert register.commands["cd"] == CdCommand
    assert register.commands["cd"].fs == file_system

    with pytest.raises(ValueError, match="Command cd already registered"):
        register.register("cd", CdCommand)


def test_get():
    file_system = FileSystem({"/": {}})
    register = Register(file_system)

    register.register("cd", CdCommand)

    assert register.get("cd") == CdCommand


def test_bad_get():
    with pytest.raises(ValueError, match="Command cd not found"):
        file_system = FileSystem({"/": {}})
        register = Register(file_system)
        register.get("cd")


def test_execute():
    file_system = FileSystem({"/": {}})
    register = Register(file_system)

    register.register("cd", CdCommand)
    assert register.execute("cd", ".") is None


def test_bad_execute():
    with pytest.raises(ValueError, match="Command cd not found"):
        file_system = FileSystem({"/": {}})
        register = Register(file_system)
        register.execute("cd", ".")
