class Greeter:
    def greet(self):
        return f"Hello, {self.name}"


class Person(Greeter):
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Croeso, {self.name}"
