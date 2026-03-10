

from typing import Generic, TypeVar, Union, Any

T = TypeVar('T', bound=Union[int, float], contravariant = True)


class Pair(Generic[T]):
    def __init__(self, a : T, b : T)-> None :
        self.a: Any = a
        self.b: Any = b

    def sum(self) -> T:
        return self.a + self.b

    def first(self) -> T:
        return self.a

    def second(self) -> T:
        return self.b

    def __iadd__(self, pair: "Pair[T]") -> "Pair[T]":
        self.a = self.a + pair.a
        self.b = self.b + pair.b
        return self


var = Pair[int](1, 2)
