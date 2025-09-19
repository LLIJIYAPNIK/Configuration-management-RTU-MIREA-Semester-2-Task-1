# Virtual Shell Emulator — CLI with Virtual Filesystem

> 🎓 Academic project for the course **"Configuration Management"**  
> 🧩 Variant 17: Shell emulator with virtual filesystem

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
![CI](https://github.com/LLIJIYAPNIK/Configuration-management-RTU-MIREA-Semester-2-Task-1/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/LLIJIYAPNIK/Configuration-management-RTU-MIREA-Semester-2-Task-1/badge.svg?branch=main)](https://coveralls.io/github/LLIJIYAPNIK/Configuration-management-RTU-MIREA-Semester-2-Task-1?branch=main)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

---

## 🚀 Quick Start

```bash
python main.py
```

→ Launches **interactive shell** with prompt like: `yourname@yourhost:~/$ `

```bash
python main.py --vfs path/to/vfs.xml --script path/to/script.txt
```

→ Executes commands from script within specified virtual filesystem.

---

## 📦 What is this project?

This is a **fully functional Unix-like shell emulator** operating within a **virtual filesystem (VFS)** loaded from an XML file.

The filesystem is **completely isolated** — all operations occur in memory, without modifying the real filesystem.

File contents are stored in **base64** — supports both text and binary data.

---

## Example VFS (XML)

```xml
<filesystem>
    <folder name="home">
        <file name="hello.txt" content="SGVsbG8gV29ybGQh" /> <!-- "Hello World!" -->
        <folder name="docs">
            <file name="readme.md" content="IyBSZWFkbWUKClRoaXMgaXMgYSB0ZXN0IGZpbGUu" />
        </folder>
    </folder>
    <file name="LICENSE" content="TGljZW5zZWQgdW5kZXIgTUlUIExpY2Vuc2U=" />
</filesystem>
```

> All files and directories are loaded into memory

---

## 📜 Example Script

```txt
cd home
ls
cd docs
ls
cd ..
cd /
ls
```

> Executed sequentially

---

## Architecture

The project is built on **three abstract classes** — the foundation of the entire system.

### 1. `Command` — base class for all commands

```python
class Command(ABC):
    command = ""          # command name (e.g., "ls")
    flags = {}            # flags (--flag)
    args = {}             # arguments (path, ...)
```

→ All commands inherit from it → `execute()` and `argparse` configured automatically.

---

### 2. `FileSystemObject` — base class for files and directories

```python
class FileSystemObject(ABC):
    def get_absolute_path(self) -> str: ...
    def rename(self, new_name) -> None: ...
    def clone(self, new_parent) -> "FileSystemObject": ...
```

→ Implemented as `File` and `Directory` — with support for copying, moving, deletion.

---

### 3. `Runner` — base class for command executors

```python
class Runner(ABC):
    def __init__(self, terminal): ...
    def run(self, *args): ...  # abstract
```

Two subclasses:
- `InteractiveRunner` — REPL mode (reads from `input()`),
- `ScriptRunner` — executes commands from file.

---

## 🗂️ File System

### `FileSystem`
- Manages object tree.
- Supports `cd`, `ls`, `mkdir`, `touch`, `rm`, `mv`, `cp` (not all commands fully implemented).
- Can save state back to XML (method exists but not exposed as command — not required by task).

### `File`
- Stores content (base64 → string).
- Supports `read()`, `write()`, `clear()`, `clone()`.

### `Directory`
- Stores children (files/folders).
- Supports `add_child()`, `remove_child()`, `get_child()`.
- Implements Pythonic interface: `__getitem__`, `__iter__`, `__len__`, etc.

---

## 💻 Terminal and Environment

### `Terminal`
- **Application session** — single instance for entire app.
- Holds `fs`, `user`, `env`, `register`.
- Processes input → delegates commands to `Register`.

### `Register`
- **Middleware** — connects commands with context.
- Registers commands → injects dependencies → executes them.

### `Environment`
- Copies variables from real OS → isolated environment.
- Supports `$VAR` syntax — variable substitution not implemented.

### `User`
- Generates prompt: `username@hostname:~/$ `
- Defaults to system data → can be overridden.

---

## XML Parser — `XmlClient`

- Reads XML → builds dictionary → `FileSystem` creates objects.
- Supports nested directories and base64 content.

---

## Launch — `main.py`

Two key functions:

```python
def parse_input(terminal):
    # Processes --vfs and --script → launches sc

def main():
    # Registers commands → launches InteractiveRunner
```

→ On startup: creates `FileSystem`, `User`, `Environment`, `Register` → starts shell.

---

## Implemented Commands

| Command | Description                                                     |
| ------- | --------------------------------------------------------------- |
| `ls`    | List files/directories                                          |
| `cd`    | Change directory                                                |
| `head`  | Show first N lines (`-n 5`)                                     |
| `tac`   | Print file in reverse order                                     |
| `wc`    | Count lines (`-I`), words (`-w`), characters (`-m`), max line (`-L`) |
| `rm`    | Remove file or directory                                        |
| `sc`    | Execute script in specified VFS (`--vfs`, `--script`)           |
| `exit`  | Exit shell                                                      |

---

## Assignment Stages — Fully Completed

### Stage 1: REPL
- ✅ Interactive mode with prompt `user@host:~/$ `
- ✅ Supports `$VAR` (environment variables)
- ✅ Error handling (unknown command, invalid arguments)
- ✅ Stub commands → now fully functional
- ✅ `exit` — clean exit

### Stage 2: Configuration
- ✅ Supports `--vfs` and `--script`
- ✅ Scripts execute with command and output display
- ✅ Error handling in scripts

### Stage 3: VFS
- ✅ XML → virtual FS in memory
- ✅ Base64 for binary data
- ✅ VFS loading error handling
- ✅ Test scripts with different nesting levels

### Stage 4: Core Commands
- ✅ `ls`, `cd` — with path and error support
- ✅ `head`, `tac`, `wc` — with flags and edge case handling

### Stage 5: Additional Commands
- ✅ `rm` — file and directory deletion
- ✅ All commands work with VFS and handle errors

---

## Testing

Project is **fully covered with tests**:

- ✅ Unit tests for all commands
- ✅ Tests for filesystem
- ✅ Tests for terminal and runners
- ✅ Integration tests
- ✅ GitHub Actions CI — style check (`black`) and tests on every push

---

## 📂 Project Structure

```
project/
├── main.py                  # Entry point
├── commands/                # All commands
├── file_system/             # FileSystem, File, Directory
├── terminal/                # Terminal, InteractiveRunner, ScriptRunner
├── abstract/                # Command, FileSystemObject, Runner
├── environment.py           # Environment
├── user.py                  # User
├── xml_parser.py            # XmlClient
├── tests/                   # All tests
└── .github/workflows/ci.yml # CI/CD
```

---

## 🚀 How to Install and Run

```bash
git clone https://github.com/your-username/Configuration-management-RTU-MIREA-Semester-2-Task-1.git
cd Configuration-management-RTU-MIREA-Semester-2-Task-1
python main.py
```

---

## License - MIT

---

## 🙏 Acknowledgments

Thanks to **Elizaveta Beltiukova** for the tip about `getpass.getuser()`!
