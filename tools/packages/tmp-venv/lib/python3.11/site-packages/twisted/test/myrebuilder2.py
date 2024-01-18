class A:
    def a(self) -> str:
        return "b"


class B(A):
    def b(self) -> str:
        return "c"


class Inherit(A):
    def a(self) -> str:
        return "d"
