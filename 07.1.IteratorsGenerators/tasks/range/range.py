from collections.abc import Iterable, Iterator, Sized


class RangeIterator(Iterator[int]):
    """The iterator class for Range"""
    def __init__(self, start: int, stop: int, step: int) -> None:
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self) -> 'RangeIterator':
        return self

    def __next__(self) -> int:
        if self.start >= self.stop and self.step > 0 or self.start <= self.stop and self.step < 0:
            raise StopIteration
        value = self.start
        self.start += self.step
        return value # todo: так ли это


class Range(Sized, Iterable[int]):
    """The range-like type, which represents an immutable sequence of numbers"""

    def __init__(self, *args: int) -> None:
        """
        :param args: either it's a single `stop` argument
            or sequence of `start, stop[, step]` arguments.
        If the `step` argument is omitted, it defaults to 1.
        If the `start` argument is omitted, it defaults to 0.
        If `step` is zero, ValueError is raised.
        """
        self._start = 0
        self._step = 1

        if len(args) == 1:
            self._stop = args[0]
        elif len(args) == 2 or len(args) == 3:
            self._start = args[0]
            self._stop = args[1]
            if len(args) == 3:
                self._step = args[2]
        else:
            raise ValueError

        if(self._step == 0):
            raise ValueError

    def __iter__(self) -> "RangeIterator":
        return RangeIterator(self._start, self._stop, self._step)

    def __repr__(self) -> str:
        s = ""
        cur_pos = self._start
        flag = False
        while cur_pos < self._stop:
            if flag:
                s += " "
            s += str(cur_pos)
            cur_pos += self._step
            flag = True
        return s

    def __str__(self) -> str:
        s =  "range(" + str(self._start) + ", " + str(self._stop)
        if self._step != 1:
            s += ", " + str(self._step)
        return s + ')'


    def __contains__(self, key: int) -> bool:
        if (self._start - key)  * (self._stop - key) < 0 and (key - self._start) % self._step == 0:
            return True
        else:
            return False

    def __getitem__(self, key: int) -> int:
        value = self._start + self._step * key
        if value >= self._stop and self._step > 0 or value <= self._stop and self._step < 0:
            raise IndexError
        return value

    def __len__(self) -> int:
        if (self._stop - self._start) * self._step < 0:
            return 0
        return abs(abs(self._stop - self._start)-1) // abs(self._step) + 1
