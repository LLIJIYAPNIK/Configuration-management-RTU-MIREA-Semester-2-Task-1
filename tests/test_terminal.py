import os
import pytest
from exceptions import UnknownCommandName
from file_system.file_system import FileSystem
from xml_parser import XmlClient
from user import User
from environment import Environment, VarEnvironmentNotFound
from commands.register import Register
from commands import CdCommand, LsCommand
from terminal.terminal import Terminal


xml_str = """
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


@pytest.fixture
def fresh_terminal():
    file_system = FileSystem(XmlClient(xml_str=xml_str).xml_dict)
    file_system.create_file_system()

    user = User("name", "hostname")
    env = Environment({"USER": "TESTNAME"})

    register = Register(file_system, user, env)
    register.register("cd", CdCommand)
    register.register("ls", LsCommand)

    return Terminal(file_system, user, env, register)


def test_get_prompt(fresh_terminal):
    assert fresh_terminal.get_prompt() == "name@hostname:~/$ "


def test_process_line_empty_and_exit(fresh_terminal):
    assert fresh_terminal.process_line("") is None
    assert fresh_terminal.process_line("exit") is None


def test_process_line_command(fresh_terminal):
    fresh_terminal.process_line("cd /home")
    assert fresh_terminal.fs.cwd.name == "home"


def test_bad_process_line_command(fresh_terminal):
    with pytest.raises(
        UnknownCommandName, match="Unknown command: unknown_command"
    ):
        fresh_terminal.process_line("unknown_command")


def test_process_line_env(fresh_terminal):
    assert fresh_terminal.process_line("$USER") is None


def test_bad_process_line_env(fresh_terminal):
    with pytest.raises(
        VarEnvironmentNotFound, match="TESTVAR not found in environment"
    ):
        fresh_terminal.process_line("$TESTVAR")
