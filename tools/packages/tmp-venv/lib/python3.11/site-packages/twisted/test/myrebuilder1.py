class A:
    def a(self) -> str:
        return "a"


class B(A):
    def b(self) -> str:
        return "b"


class Inherit(A):
    def a(self) -> str:
        return "c"
