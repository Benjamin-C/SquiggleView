from typing import Callable

class Parameter():
    def __init__(self, value: any = None, default: any = "", retype: Callable = lambda x: x, sender: Callable = str):
        self.value = value or default
        self.default = default
        self.retype = retype
        self.sender = sender

    def setValue(self, newval: any):
        self.value = self.retype(newval)

    def getSendValue(self):
        return self.sender(self.value)