from abstract.runner import Runner


class InteractiveRunner(Runner):
    def run(self):
        while self.terminal.is_running:
            try:
                line = input(self.terminal.get_prompt())
                self.terminal.process_line(line)
            except (KeyboardInterrupt, EOFError):
                print()
                break
            except Exception as e:
                print(e)
