from abstract import Runner


class ScriptRunner(Runner):
    def run(self, script_path: str):
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        print(f"{self.terminal.get_prompt()}{line}")
                        self.terminal.process_line(line)
                    except Exception as e:
                        print(f"Error on line {line_num}: {e}")
        except FileNotFoundError:
            print(f"Script file not found: {script_path}")
