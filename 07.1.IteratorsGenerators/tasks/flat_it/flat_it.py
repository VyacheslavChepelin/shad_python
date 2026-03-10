from collections.abc import Iterable, Iterator
from typing import Any

def flat_it(sequence: Iterable[Any]) -> Iterator[Any]:
    """
    :param sequence: iterable with arbitrary level of nested iterables
    :return: generator producing flatten sequence
    """

    def gen(seq: Iterable[Any]):
        for item in seq:
            if isinstance(item, Iterable):
                if isinstance(item, str):
                    for cur in item:
                        yield from cur
                else:
                    for cur in gen(item):
                        yield cur
            else:
                yield item

    return iter(gen(sequence))

