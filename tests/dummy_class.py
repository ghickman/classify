class DummyParent:
    def one(self):
        print("one parent")

    def three(self):
        pass


class DummyClass(DummyParent):
    def __init__(self):
        super().__init__()

    def _internal(self):
        pass

    def one(self):
        super().one()
        print("one child")

    def two(self):
        pass
