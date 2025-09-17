import argparse

from commands.register import Register

from commands import CdCommand, LsCommand, ScCommand
from xml_parser import XmlClient
from user import User
from environment import Environment

from file_system import FileSystem
from terminal.terminal import Terminal
from terminal.interactive import InteractiveRunner


XML_STR = """
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


def parse_input(terminal: Terminal):
    parser = argparse.ArgumentParser()

    parser.add_argument("--vfs")
    parser.add_argument("--script")

    args = parser.parse_args()

    if args.vfs and args.script:
        try:
            terminal.process_line(
                f"sc --vfs {args.vfs} --script {args.script}"
            )
        except FileExistsError as e:
            print(e)


def main():
    register_command.register("cd", CdCommand)
    register_command.register("ls", LsCommand)
    register_command.register("sc", ScCommand)
    parse_input(terminal)
    runner = InteractiveRunner(terminal)
    runner.run()


if __name__ == "__main__":
    fs = FileSystem(XmlClient(xml_str=XML_STR).xml_dict)
    fs.create_file_system()

    user = User()
    env = Environment()

    register_command = Register(fs, user, env)
    terminal = Terminal(fs, user, env, register_command)
    register_command.terminal = terminal

    main()
