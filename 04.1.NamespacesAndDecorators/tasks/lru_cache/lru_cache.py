import functools
from collections.abc import Callable
from typing import Any, TypeVar, OrderedDict

Function = TypeVar('Function', bound=Callable[..., Any])



def cache(max_size: int) -> Callable[[Function], Function]:
    """
    Returns decorator, which stores result of function
    for `max_size` most recent function arguments.
    :param max_size: max amount of unique arguments to store values for
    :return: decorator, which wraps any function passed
    """
    def cache_decorator(function):
        cache_lines = OrderedDict()
        @functools.wraps(function)
        def wrapper(*args: Any) -> Any:
            if args in cache_lines:
                return cache_lines[args]
            result = function(*args)
            if args in cache_lines:
                return result
            if len(cache_lines) == max_size:
                cache_lines.popitem(last = False)
            cache_lines[args] = result
            return result
        return wrapper

    return cache_decorator
