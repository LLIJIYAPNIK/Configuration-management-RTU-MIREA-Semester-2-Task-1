from base.command import Command


class TestCommand(Command):
    """Test command for unit tests"""

    __test__ = False

    command = "test"
    command_description = "Test command for unit tests"
    flags = {
        "--verbose": {"action": "store_true", "help": "Enable verbose output"},
        "--count": {"default": 1, "help": "Number of times to run"},
    }
    args = {
        "filename": {
            "help": "Input file name",
            "nargs": "?",
            "default": "default.txt",
        },
    }

    def execute(self):
        pass

    def get_help(self):
        pass


def test_command_parser_initialization():
    cmd = TestCommand()

    assert cmd.parser is not None
    assert cmd.parser.prog == "test"
    assert cmd.parser.description == "Test command for unit tests"

    assert cmd.parser.exit_on_error is False


def test_command_register_args():
    cmd = TestCommand()

    actions = {action.dest: action for action in cmd.parser._actions}

    assert "filename" in actions
    filename_action = actions["filename"]
    assert filename_action.help == "Input file name"
    assert filename_action.nargs == "?"
    assert filename_action.default == "default.txt"

    assert "verbose" in actions
    verbose_action = actions["verbose"]
    assert verbose_action.help == "Enable verbose output"
    assert verbose_action.default is False
    assert verbose_action.const is True

    assert "count" in actions
    count_action = actions["count"]
    assert count_action.help == "Number of times to run"
    assert count_action.default == 1
