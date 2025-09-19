import pytest
from unittest.mock import patch, Mock
from main import initialize_system, register_commands, parse_input


@pytest.fixture
def mock_file_system():
    fs = Mock()
    fs.create_file_system = Mock()
    return fs


@pytest.fixture
def mock_xml_client():
    with patch("main.XmlClient") as mock:
        mock_instance = Mock()
        mock_instance.xml_dict = {"/": {}}  # ← добавь корневой ключ!
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_user():
    with patch("main.User") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_environment():
    with patch("main.Environment") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_register():
    with patch("main.Register") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_terminal():
    """Мок Terminal."""
    with patch("main.Terminal") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


def test_initialize_system(
    mock_xml_client, mock_user, mock_environment, mock_register, mock_terminal
):
    fs, user, env, register, terminal = initialize_system()

    mock_xml_client.assert_called_once_with("vfs.xml")
    assert fs.create_file_system
    assert isinstance(user, Mock)
    assert isinstance(env, Mock)
    assert isinstance(register, Mock)
    assert isinstance(terminal, Mock)
    assert register.terminal == terminal


def test_register_commands(mock_register):
    from commands import (
        CdCommand,
        LsCommand,
        ScCommand,
        HeadCommand,
        TacCommand,
        WcCommand,
        RmCommand,
    )

    register_commands(mock_register)

    expected_calls = [
        ("cd", CdCommand),
        ("ls", LsCommand),
        ("sc", ScCommand),
        ("head", HeadCommand),
        ("tac", TacCommand),
        ("wc", WcCommand),
        ("rm", RmCommand),
    ]

    for cmd_name, cmd_class in expected_calls:
        mock_register.register.assert_any_call(cmd_name, cmd_class)

    assert mock_register.register.call_count == len(expected_calls)


@patch("main.argparse.ArgumentParser")
def test_parse_input_with_vfs_and_script(mock_parser, mock_terminal):
    mock_args = Mock()
    mock_args.vfs = "test_vfs.xml"
    mock_args.script = "test_script.txt"
    mock_parser.return_value.parse_args.return_value = mock_args

    parse_input(mock_terminal)

    mock_terminal.process_line.assert_called_once_with(
        "sc --vfs test_vfs.xml --script test_script.txt"
    )


@patch("main.argparse.ArgumentParser")
def test_parse_input_without_args(mock_parser, mock_terminal):
    mock_args = Mock()
    mock_args.vfs = None
    mock_args.script = None
    mock_parser.return_value.parse_args.return_value = mock_args

    parse_input(mock_terminal)

    mock_terminal.process_line.assert_not_called()


@patch("main.argparse.ArgumentParser")
def test_parse_input_with_file_exists_error(mock_parser, mock_terminal):
    mock_args = Mock()
    mock_args.vfs = "test_vfs.xml"
    mock_args.script = "test_script.txt"
    mock_parser.return_value.parse_args.return_value = mock_args

    mock_terminal.process_line.side_effect = FileExistsError("Test error")

    with patch("builtins.print") as mock_print:
        parse_input(mock_terminal)
        mock_print.assert_called_once()
        printed_arg = mock_print.call_args[0][0]
        assert str(printed_arg) == "Test error"
