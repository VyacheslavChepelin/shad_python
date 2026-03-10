from typing import TypeVar, Protocol

T = TypeVar('T')
T2 = TypeVar('T2')
T3 = TypeVar('T3', float, bool, int, contravariant=True)
class MyProtocol(Protocol[T, T2, T3]):
    def __call__(self, a: T, b : T, c : T2) -> T3: ...


def f(a: MyProtocol[T, T2, T3], b: T, c: T, d: T2) -> T3:
    return a(b, c, d)


TEST_SAMPLES = """
# SUCCESS
def g(a: float, b: float, c: complex) -> int:
    return 1

f(g, 1, 4.5, 1j)

# SUCCESS
def g(a: complex, b: complex, c: complex) -> bool:
    return True

f(g, 1, 4, True)

# ERROR
def g(a: bool, b: float, c: complex) -> int:
    return 1

f(g, 1, 4.5, 1j)

# ERROR
def g(a: int, b: int, c: complex) -> int:
    return 1

f(g, 1, 4.5, 1j)

# ERROR
def g(a: int, b: float, c: float) -> int:
    return 1

f(g, 1, 4.5, 1j)

# SUCCESS
def g(a: float, b: float, c: complex) -> float:
    return 1.0

f(g, True, True, True)

# ERROR
def g(a: float, b: float, c: complex) -> complex:
    return 1j

f(g, True, True, True)
"""
