import datetime as dt
import functools

def profiler(func):  # type: ignore
    """
    Returns profiling decorator, which counts calls of function
    and measure last function execution time.
    Results are stored as function attributes: calls, last_time_taken
    :param func: function to decorate
    :return: decorator, which wraps any function passed
    """
    recursion_length = 0
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal recursion_length
        cur_rec_length = recursion_length

        begin_time = dt.datetime.now()
        result = func(*args, **kwargs)

        recursion_length += 1
        end_time = dt.datetime.now()
        wrapper.last_time_taken = (end_time - begin_time).total_seconds()
        wrapper.calls = recursion_length - cur_rec_length
        return result

    return wrapper
