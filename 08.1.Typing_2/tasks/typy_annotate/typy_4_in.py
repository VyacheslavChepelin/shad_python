from typing import TypeVar, Protocol

T = TypeVar('T', contravariant=True)
class MyProtocol(Protocol[T]):
    def __contains__(self, item: T) -> bool: ...

T2 = TypeVar('T2', contravariant=True, bound=MyProtocol)

def f(a: T2, b: T) -> T | None :
    return b if b in a else None


TEST_SAMPLES = """
# SUCCESS

a: float | None
a = f([1, 2, 3], 1)
if a is not None:
    a += 1

# SUCCESS
a: float | None
a = f({1, 2, 3}, 1)


# SUCCESS
a: str | None
fix: str = "abcd"
a = f(fix, "a")


# SUCCESS
class A:
    def __contains__(self, a: object) -> bool:
        return True

a: int | None
a = f(A(), 10)

b: str | None
b = f(A(), "qwerty")

"""
