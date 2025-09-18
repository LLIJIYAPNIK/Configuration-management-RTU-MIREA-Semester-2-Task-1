import pytest
from unittest.mock import Mock, patch
from commands.sc import ScCommand
from user import User
from environment import Environment
from commands.register import Register
from terminal.terminal import Terminal


@pytest.fixture
def mock_terminal():
    terminal = Mock(spec=Terminal)
    terminal.fs = None
    terminal.register = None
    return terminal


@pytest.fixture
def sc_command(mock_terminal):
    user = User("test", "host")
    env = Environment()
    register = Register(..., user, env)
    register.terminal = mock_terminal
    register.commands = {}

    cmd = ScCommand()
    cmd.user = user
    cmd.env = env
    cmd.register = register
    return cmd


@patch("os.path.exists")
@patch("commands.sc.XmlClient")
@patch("commands.sc.FileSystem")
@patch("commands.sc.ScriptRunner")
def test_sc_command_success(
    mock_script_runner,
    mock_file_system,
    mock_xml_client,
    mock_os_path_exists,
    sc_command,
    mock_terminal,
):
    mock_os_path_exists.side_effect = lambda path: path in [
        "/fake/vfs.xml",
        "/fake/script.txt",
    ]

    mock_fs_instance = Mock()
    mock_file_system.return_value = mock_fs_instance

    mock_xml_instance = Mock()
    mock_xml_instance.xml_dict = {"mock": "dict"}
    mock_xml_client.return_value = mock_xml_instance

    mock_runner_instance = Mock()
    mock_script_runner.return_value = mock_runner_instance

    sc_command.execute(
        ["--vfs", "/fake/vfs.xml", "--script", "/fake/script.txt"]
    )

    mock_os_path_exists.assert_any_call("/fake/vfs.xml")
    mock_os_path_exists.assert_any_call("/fake/script.txt")

    mock_file_system.assert_called_once_with({"mock": "dict"})
    mock_fs_instance.create_file_system.assert_called_once()

    assert sc_command.register.terminal.fs == mock_fs_instance
    assert sc_command.register.terminal.register is not None

    mock_script_runner.assert_called_once_with(sc_command.register.terminal)
    mock_runner_instance.run.assert_called_once_with("/fake/script.txt")


@patch("os.path.exists")
def test_sc_command_vfs_not_found(mock_os_path_exists, sc_command):
    mock_os_path_exists.return_value = False

    with pytest.raises(
        FileExistsError, match="VFS not found. Check your path to VFS."
    ):
        sc_command.execute(
            ["--vfs", "/nonexistent.xml", "--script", "/fake/script.txt"]
        )


@patch("os.path.exists")
def test_sc_command_script_not_found(mock_os_path_exists, sc_command):
    def side_effect(path):
        if path == "/fake/vfs.xml":
            return True
        return False

    mock_os_path_exists.side_effect = side_effect

    with pytest.raises(
        FileNotFoundError, match="No such file or directory: '/fake/vfs.xml"
    ):
        sc_command.execute(
            ["--vfs", "/fake/vfs.xml", "--script", "/nonexistent.txt"]
        )


@patch("os.path.exists")
@patch("commands.sc.XmlClient")
@patch("commands.sc.FileSystem")
def test_sc_command_register_reconfigured(
    mock_file_system,
    mock_xml_client,
    mock_os_path_exists,
    sc_command,
):
    mock_os_path_exists.return_value = True

    mock_fs_instance = Mock()
    mock_file_system.return_value = mock_fs_instance

    mock_xml_instance = Mock()
    mock_xml_instance.xml_dict = {"mock": "dict"}
    mock_xml_client.return_value = mock_xml_instance

    class MockCommand:
        fs = None

    mock_cmd = MockCommand()
    sc_command.register.commands["test"] = mock_cmd

    sc_command.execute(
        ["--vfs", "/fake/vfs.xml", "--script", "/fake/script.txt"]
    )

    new_register = sc_command.register.terminal.register
    assert "test" in new_register.commands

    assert new_register.commands["test"].fs == mock_fs_instance


def test_sc_command_get_help(sc_command):
    assert "sc - start command" in sc_command.get_help()
