from contextlib import contextmanager
from typing import Iterator, TextIO, Type
import sys

@contextmanager
def supresser(*types_: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except types_:
        pass



@contextmanager
def retyper(type_from: Type[BaseException], type_to: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except type_from as e:
        exception = type_to()
        exception.args = e.args
        exception.__traceback__ = e.__traceback__
        raise exception


@contextmanager
def dumper(stream: TextIO | None = None) -> Iterator[None]:
    try:
        yield
    except BaseException as e:
        if stream is not None:
            stream.write(str(e))
        else:
            sys.stderr.write(str(e))
        raise
