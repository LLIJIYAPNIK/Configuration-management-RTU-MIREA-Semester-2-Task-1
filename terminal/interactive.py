from abstract.runner import Runner
from exceptions import UnknownCommandName


class InteractiveRunner(Runner):
    def run(self):
        while self.terminal.is_running:
            try:
                line = input(self.terminal.get_prompt())
                self.terminal.process_line(line)
            except (KeyboardInterrupt, EOFError):
                print()
                break
            except UnknownCommandName as e:
                print(e)
            except Exception as e:
                print(e)
