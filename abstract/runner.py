from abc import ABC, abstractmethod


class Runner(ABC):
    def __init__(self, terminal):
        self.terminal = terminal

    @abstractmethod
    def run(self, *args):
        pass
