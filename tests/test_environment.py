import pytest
import os
from environment import Environment, VarEnvironmentNotFound


def test_environment_creation():
    user_env = {"USER": "test_user"}
    env = Environment(user_env)
    assert env.environment == user_env

    env = Environment()
    assert env.environment == os.environ.copy()


def test_environment_get():
    user_env = {"USER": "test_user"}
    env = Environment(user_env)
    assert env.get("USER") == "test_user"


def test_bad_environment_get():
    with pytest.raises(
        VarEnvironmentNotFound, match="SOMETHING not found in environment"
    ):
        Environment().get("SOMETHING")


def test_environment_set():
    user_env = {"USER": "test_user"}
    env = Environment(user_env)
    assert env.set("USER", "new_user") == "Success"


def test_bad_environment_set():
    with pytest.raises(
        VarEnvironmentNotFound, match="SOMETHING not found in environment"
    ):
        Environment().get("SOMETHING")
