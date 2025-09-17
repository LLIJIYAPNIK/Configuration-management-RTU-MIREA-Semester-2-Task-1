import pytest
from unittest.mock import patch
from file_system.file_system import FileSystem
from terminal.script import ScriptRunner
from xml_parser import XmlClient
from user import User
from environment import Environment
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
    fs = FileSystem(XmlClient(xml_str=xml_str).xml_dict)
    fs.create_file_system()
    user = User("testuser", "host")
    env = Environment({"USER": "TESTUSER"})
    register = Register(fs, user, env)
    register.register("cd", CdCommand)
    register.register("ls", LsCommand)
    return Terminal(fs, user, env, register)


@pytest.fixture
def script_file(tmp_path):
    def _create(lines):
        file_path = tmp_path / "script.txt"
        file_path.write_text("\n".join(lines), encoding="utf-8")
        return str(file_path)

    return _create


def test_script_runner_executes_commands(fresh_terminal, script_file):
    script = script_file(["cd home", "cd docs"])

    runner = ScriptRunner(fresh_terminal)
    runner.run(script)

    assert fresh_terminal.fs.cwd.name == "docs"


def test_script_runner_ignores_empty_lines_and_comments(
    fresh_terminal, script_file
):
    script = script_file(
        ["cd home", "", "# Это комментарий", "   \t  ", "cd docs"]
    )

    runner = ScriptRunner(fresh_terminal)
    runner.run(script)

    assert (
        fresh_terminal.fs.cwd.name == "docs"
    )


def test_script_runner_prints_prompt_and_command(
    capsys, fresh_terminal, script_file
):
    with patch.object(fresh_terminal, "get_prompt", return_value="PROMPT> "):
        script = script_file(["cd home", "ls"])

        runner = ScriptRunner(fresh_terminal)
        runner.run(script)

    captured = capsys.readouterr()

    assert "PROMPT> cd home\n" in captured.out
    assert "PROMPT> ls\n" in captured.out


def test_script_runner_unknown_command_shows_line_number(
    capsys, fresh_terminal, script_file
):
    script = script_file(["cd home", "unknown_cmd", "cd docs"])  # ← строка 2

    runner = ScriptRunner(fresh_terminal)
    runner.run(script)

    captured = capsys.readouterr()
    assert "Error on line 2: Unknown command: unknown_cmd" in captured.out

    assert fresh_terminal.fs.cwd.name == "docs"


def test_script_runner_file_not_found_shows_error(capsys, fresh_terminal):
    runner = ScriptRunner(fresh_terminal)
    runner.run("nonexistent_script.txt")

    captured = capsys.readouterr()
    assert "Script file not found: nonexistent_script.txt" in captured.out


def test_script_runner_exit_command_stops_execution(
    fresh_terminal, script_file
):
    script = script_file(
        ["cd home", "exit", "cd docs"]
    )

    runner = ScriptRunner(fresh_terminal)
    runner.run(script)

    assert fresh_terminal.fs.cwd.name == "home"
    assert (
        fresh_terminal.is_running is False
    )


def test_script_runner_continues_after_error(fresh_terminal, script_file):
    script = script_file(["cd home", "invalid_command", "cd docs"])

    runner = ScriptRunner(fresh_terminal)
    runner.run(script)

    assert fresh_terminal.fs.cwd.name == "docs"


def test_script_runner_calls_get_prompt_for_each_command(
    fresh_terminal, script_file
):
    with patch.object(
        fresh_terminal, "get_prompt", return_value="> "
    ) as mock_prompt:
        script = script_file(["cd home", "ls", "cd docs"])

        runner = ScriptRunner(fresh_terminal)
        runner.run(script)

    assert mock_prompt.call_count == 3
