from typing import TypeVar, Protocol

T_co = TypeVar('T_co', covariant=True)


class Gettable(Protocol[T_co]):
    def __getitem__(self, item: int) -> T_co: ...
    def __len__(self) -> int: ...


def get(container : Gettable[T_co], index: int) -> T_co | None:
    if container:
        return container[index]

    return None
