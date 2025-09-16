from file_system import FileSystem
from user import User


def test_user_creation():
    name = "Alex"
    hostname = "desktop"

    user = User(name, hostname)

    assert user.name == name and user.hostname == hostname

    user = User()
    assert user.name != name and user.hostname != hostname


def test_get_user_for_shell():
    test_tree = {
        "/": {
            "home": {"file1.txt": "Hello", "docs": {"readme.md": "# Readme"}},
            "tmp": {},
            "LICENSE": "MIT",
        }
    }

    fs = FileSystem(test_tree)
    fs.create_file_system()

    user = User("Alex", "desktop")
    assert (
        user.get_user_for_shell(fs.cwd) == f"{user.name}@{user.hostname}:~/$ "
    )

    fs.cd("/home")
    assert (
        user.get_user_for_shell(fs.cwd)
        == f"{user.name}@{user.hostname}:~/home$ "
    )


def test_str():
    user = User("Alex", "desktop")
    assert str(user) == f"{user.name}@{user.hostname}"
    assert "@" in str(User())
