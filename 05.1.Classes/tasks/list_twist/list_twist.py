from collections import UserList
import typing as tp


class ListTwist(UserList[tp.Any]):
    """
    List-like class with additional attributes:
        * reversed, R - return reversed list
        * first, F - insert or retrieve first element;
                     Undefined for empty list
        * last, L -  insert or retrieve last element;
                     Undefined for empty list
        * size, S -  set or retrieve size of list;
                     If size less than list length - truncate to size;
                     If size greater than list length - pad with Nones
    """
    data = []

    def __init__(self, data: tp.Iterable[tp.Any] = []) -> None:
        super().__init__()
        for item in data:
            self.data.append(item)

    def __getattr__(self, name: str) -> tp.Any:
        if name == 'reversed' or name == 'R':
            return self.data[::-1]
        elif name == 'first' or name == 'F':
            if len(self.data) == 0:
                return None
            return self.data[0]
        elif name == 'last' or name == 'L':
            if len(self.data) == 0:
                return None
            return self.data[-1]
        elif name == 'size' or name == 'S':
            return len(self.data)
        return self.__dict__.get(name, 0)

    def __setattr__(self, name: str, value: tp.Any) -> None:
        if name == 'first' or name == 'F':
            self.data[0] = value
        elif name == 'last' or name == 'L':
           self.data[-1] = value
        elif name == 'size' or name == 'S':
            while len(self.data) < value:
                self.data.append(None)
            while len(self.data) > value:
                self.data.pop()
        else:
            self.__dict__[name] = value
