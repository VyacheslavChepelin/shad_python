import time
from types import NoneType

class TimeoutException(Exception):
    pass

class SoftTimeoutException(TimeoutException):
    pass

class HardTimeoutException(TimeoutException):
    pass

class TimeCatcher:
    def __init__(self, / , soft_timeout  = None, hard_timeout  = None):
        assert soft_timeout is None or soft_timeout > 0
        assert hard_timeout is None or hard_timeout > 0
        assert (soft_timeout is None or hard_timeout is None or soft_timeout <= hard_timeout)
        self.soft_timeout = soft_timeout
        self.hard_timeout = hard_timeout
    def __enter__(self):
        self.time_start = time.time()
        return self
    def cur_time(self):
        return float(time.time() - self.time_start)
    def __exit__(self, *args):
        if self.soft_timeout != -1 or self.hard_timeout != -1:
            time = self.cur_time()
            if isinstance(time, NoneType):
                return False
            if self.hard_timeout is not None and time > self.hard_timeout:
                raise HardTimeoutException()
            if self.soft_timeout is not None and time > self.soft_timeout:
                raise SoftTimeoutException()
        return None

    def __str__(self):
        return "Time consumed: " + str(self.cur_time())

    def __float__(self):
        return float(self.cur_time())
