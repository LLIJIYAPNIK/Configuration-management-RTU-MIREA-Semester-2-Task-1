import pytest
from unittest.mock import patch
from file_system.file_system import FileSystem
from terminal import InteractiveRunner
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


def test_interactive_runner_known_command_executed(fresh_terminal):
    fresh_terminal.fs.cwd = fresh_terminal.fs.root.get_child("home")

    with patch(
        "builtins.input", side_effect=["cd ..", EOFError()]
    ) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    assert mock_input.call_count == 2
    assert fresh_terminal.fs.cwd.name == "/"
    assert fresh_terminal.is_running is True


def test_interactive_runner_exit_command_stops_loop(fresh_terminal):
    with patch("builtins.input", side_effect=["exit"]) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    assert mock_input.call_count == 1
    assert fresh_terminal.is_running is False


def test_interactive_runner_empty_input_ignored_prompt_shown_again(
    fresh_terminal,
):
    with patch.object(
        fresh_terminal, "get_prompt", return_value="PROMPT> "
    ) as mock_prompt:
        with patch("builtins.input", side_effect=["", "exit"]) as mock_input:
            runner = InteractiveRunner(fresh_terminal)
            runner.run()

    assert mock_prompt.call_count == 2
    assert mock_input.call_count == 2
    assert fresh_terminal.is_running is False


def test_interactive_runner_keyboard_interrupt_breaks_loop(
    capsys, fresh_terminal
):
    with patch(
        "builtins.input", side_effect=[KeyboardInterrupt]
    ) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    captured = capsys.readouterr()
    assert "\n" in captured.out
    assert mock_input.call_count == 1
    assert fresh_terminal.is_running is True


def test_interactive_runner_eof_error_breaks_loop(capsys, fresh_terminal):
    with patch("builtins.input", side_effect=[EOFError]) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    captured = capsys.readouterr()
    assert "\n" in captured.out
    assert mock_input.call_count == 1
    assert fresh_terminal.is_running is True


def test_interactive_runner_env_variable_expansion(capsys, fresh_terminal):
    with patch("builtins.input", side_effect=["$USER", "exit"]) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    captured = capsys.readouterr()
    assert "TESTUSER\n" in captured.out
    assert mock_input.call_count == 2
    assert fresh_terminal.is_running is False


def test_interactive_runner_unknown_command_shows_error_and_continues(
    capsys, fresh_terminal
):
    with patch(
        "builtins.input", side_effect=["unknown_cmd", "exit"]
    ) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    captured = capsys.readouterr()
    assert "Unknown command: unknown_cmd" in captured.out
    assert mock_input.call_count == 2
    assert fresh_terminal.is_running is False


def test_interactive_runner_whitespace_input_ignored(fresh_terminal):
    with patch.object(
        fresh_terminal, "get_prompt", return_value="PROMPT> "
    ) as mock_prompt:
        with patch(
            "builtins.input", side_effect=["   \t  ", "exit"]
        ) as mock_input:
            runner = InteractiveRunner(fresh_terminal)
            runner.run()

    assert mock_prompt.call_count == 2
    assert mock_input.call_count == 2
    assert fresh_terminal.is_running is False


def test_interactive_runner_nonexistent_env_variable_prints_empty(
    capsys, fresh_terminal
):
    with patch(
        "builtins.input", side_effect=["$NONEXISTENT", "exit"]
    ) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    captured = capsys.readouterr()
    assert "\n" in captured.out
    assert "$NONEXISTENT" not in captured.out
    assert mock_input.call_count == 2


def test_interactive_runner_multiple_commands_in_sequence(fresh_terminal):
    fresh_terminal.fs.cwd = fresh_terminal.fs.root

    with patch(
        "builtins.input", side_effect=["cd home", "cd docs", "cd ..", "exit"]
    ) as mock_input:
        runner = InteractiveRunner(fresh_terminal)
        runner.run()

    assert fresh_terminal.fs.cwd.name == "home"
    assert mock_input.call_count == 4
    assert fresh_terminal.is_running is False
