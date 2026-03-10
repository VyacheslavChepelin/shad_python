import string
from abc import abstractmethod, ABC
import typing as tp
from collections import defaultdict
from itertools import groupby
import heapq

TRow = dict[str, tp.Any]
TRowsIterable = tp.Iterable[TRow]
TRowsGenerator = tp.Generator[TRow, None, None]


class Operation(ABC):
    @abstractmethod
    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        pass


class Read(Operation):
    def __init__(self, filename: str, parser: tp.Callable[[str], TRow]) -> None:
        self._filename = filename
        self._parser = parser

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        with open(self._filename) as f:
            for line in f:
                yield self._parser(line)


class ReadIterFactory(Operation):
    def __init__(self, name: str) -> None:
        self._name = name

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in kwargs[self._name]():
            yield row


# Operations


class Mapper(ABC):
    """Base class for mappers"""
    @abstractmethod
    def __call__(self, row: TRow) -> TRowsGenerator:
        """
        :param row: one table row
        """
        pass


class Map(Operation):
    def __init__(self, mapper: Mapper) -> None:
        self._mapper = mapper

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in rows:
            for item in self._mapper(row):
                yield item



class Reducer(ABC):
    """Base class for reducers"""
    @abstractmethod
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        """
        :param rows: table rows
        """
        pass


class Reduce(Operation):
    def __init__(self, reducer: Reducer, keys: tp.Sequence[str]) -> None:
        self._reducer = reducer
        self._keys = keys

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for k, row_group in groupby(rows, lambda x: tuple(x.get(key) for key in self._keys)):
            for item in self._reducer(tuple(self._keys), row_group):
                yield item





class Joiner(ABC):
    """Base class for joiners"""
    def __init__(self, suffix_a: str = '_1', suffix_b: str = '_2') -> None:
        self._a_suffix = suffix_a
        self._b_suffix = suffix_b

    @abstractmethod
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        """
        :param keys: join keys
        :param rows_a: left table rows
        :param rows_b: right table rows
        """
        pass



def log_output(left, right):
    f = True
    if f:
        print("Cur:")
        print(list(left))
        print(list(right))
        print()


class Join(Operation):
    def __init__(self, joiner: Joiner, keys: tp.Sequence[str]):
        self._keys = keys
        self._joiner = joiner

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        def get_key_row(row):
            if row is None:
                return None
            return tuple(row[key] for key in self._keys)

        left_iter = iter(rows)
        right_iter = iter(args[0])
        left_row = next(left_iter)
        right_row = next(right_iter)

        def left_generator(current_key):
            nonlocal left_row
            nonlocal left_iter
            if left_row is None:
                return
            while left_row is not None and get_key_row(left_row) == current_key:
                yield left_row
                left_row = next(left_iter, None)

        def right_generator(current_key):
            nonlocal right_row
            nonlocal right_iter
            if right_row is None:
                return
            while right_row is not None and get_key_row(right_row) == current_key:
                yield right_row
                right_row = next(right_iter, None)

        while left_row is not None or right_row is not None:
            left_key = get_key_row(left_row)
            right_key = get_key_row(right_row)
            left_gen = iter([])
            right_gen = iter([])
            if left_key == right_key:
                left_gen = left_generator(left_key)
                right_gen = right_generator(right_key)
            elif left_key is not None and right_key is not None and left_key < right_key:
                left_gen = left_generator(left_key)
            elif left_key is not None and right_key is not None and left_key > right_key:
                right_gen = right_generator(right_key)
            elif left_key is None and right_key is not None:
                right_gen = right_generator(right_key)
            elif left_key is not None and right_key is None:
                left_gen = left_generator(left_key)
            # log_output(left_gen, right_gen)
            for item in self._joiner(self._keys, left_gen, right_gen):
                 yield item


# Dummy operatorsleft


class DummyMapper(Mapper):
    """Yield exactly the row passed"""
    def __call__(self, row: TRow) -> TRowsGenerator:
        yield row


class FirstReducer(Reducer):
    """Yield only first row from passed ones"""
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        for row in rows:
            yield row
            break


# Mappers


class FilterPunctuation(Mapper):
    """Left only non-punctuation symbols"""
    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        row[self._column] = row[self._column].translate(str.maketrans('', '', string.punctuation))
        yield row


class LowerCase(Mapper):
    """Replace column value with value in lower case"""
    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        row[self._column] = row[self._column].lower()
        yield row


def my_generator_split(s:str, separator: str | None):
    start = 0
    if separator is None:
        while start < len(s):
            if s[start].isspace():
                start += 1
                continue
            end = start
            while end < len(s) and not s[end].isspace():
                end += 1
            yield s[start:end]
            start = end
    else:
        while start < len(s):
            idx = s.find(separator, start)
            if idx == -1:
                yield s[start:]
                break
            yield s[start:idx]
            start = idx + len(separator)

class Split(Mapper):
    """Split row on multiple rows by separator"""
    def __init__(self, column: str, separator: str | None = None) -> None:
        """
        :param column: name of column to split
        :param separator: string to separate by
        """
        self._column = column
        self._separator = separator

    def __call__(self, row: TRow) -> TRowsGenerator:
        s = row[self._column]
        for part in my_generator_split(s, self._separator):
            row[self._column] = part
            yield row.copy()


class Product(Mapper):
    """Calculates product of multiple columns"""
    def __init__(self, columns: tp.Sequence[str], result_column: str = 'product') -> None:
        """
        :param columns: column names to product
        :param result_column: column name to save product in
        """
        self._columns = columns
        self._result_column = result_column

    def __call__(self, row: TRow) -> TRowsGenerator:
        product = 1
        for column in self._columns:
            product *= row[column]
        row[self._result_column] = product
        yield row


class Filter(Mapper):
    """Remove records that don't satisfy some condition"""
    def __init__(self, condition: tp.Callable[[TRow], bool]) -> None:
        """
        :param condition: if condition is not true - remove record
        """
        self._condition = condition

    def __call__(self, row: TRow) -> TRowsGenerator:
        if self._condition(row):
            yield row


class Project(Mapper):
    """Leave only mentioned columns"""
    def __init__(self, columns: tp.Sequence[str]) -> None:
        """
        :param columns: names of columns
        """
        self._columns = columns

    def __call__(self, row: TRow) -> TRowsGenerator:
        need_to_del = []
        for column in row.keys():
            if column not in self._columns:
                need_to_del.append(column)
        for column in need_to_del:
            del row[column]
        yield row


# Reducers


class TopN(Reducer):
    """Calculate top N by value"""
    def __init__(self, column: str, n: int) -> None:
        """
        :param column: column name to get top by
        :param n: number of top values to extract
        """
        self._column_max = column
        self._n = n

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        heap = []
        ind = 1
        for row in rows:
            if len(heap) < self._n:
                heapq.heappush(heap, (row[self._column_max], ind, row))
            elif len(heap) == self._n:
                if row[self._column_max] > heap[0][0]:
                    heapq.heappop(heap)
                    heapq.heappush(heap, (row[self._column_max], ind, row))
            ind += 1
        top_rows = [heapq.heappop(heap)[2] for i in range(len(heap))]
        for row in sorted(top_rows, key=lambda x: tuple(x[col] for col in group_key)):
            yield row


class TermFrequency(Reducer):
    """Calculate frequency of values in column"""
    def __init__(self, words_column: str, result_column: str = 'tf') -> None:
        """
        :param words_column: name for column with words
        :param result_column: name for result column
        """
        self._words_column = words_column
        self._result_column = result_column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        f = False
        word_map = defaultdict(int)
        sum = 0
        answer = {}
        for row in rows:
            if not f:
                f = True
                for key in group_key:
                    answer[key] = row[key]
            word_map[row[self._words_column]] += 1
            sum += 1

        for k, v in word_map.items():
            answer[self._result_column] = v / sum
            answer[self._words_column] = k
            yield answer.copy()


class Count(Reducer):
    """
    Count records by key
    Example for group_key=('a',) and column='d'
        {'a': 1, 'b': 5, 'c': 2}
        {'a': 1, 'b': 6, 'c': 1}
        =>
        {'a': 1, 'd': 2}
    """
    def __init__(self, column: str) -> None:
        """
        :param column: name for result column
        """
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        f = False
        answer = {}
        for row in rows:
            if not f:
                f = True
                for key in group_key:
                    answer[key] = row[key]
                answer[self._column] = 1
            elif f:
                answer[self._column] += 1

        yield answer


class Sum(Reducer):
    """
    Sum values aggregated by key
    Example for key=('a',) and column='b'
        {'a': 1, 'b': 2, 'c': 4}
        {'a': 1, 'b': 3, 'c': 5}
        =>
        {'a': 1, 'b': 5}
    """
    def __init__(self, column: str) -> None:
        """
        :param column: name for sum column
        """
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        f = False
        answer = {}
        for row in rows:
            if not f:
                f = True
                for key in group_key:
                    answer[key] = row[key]
                answer[self._column] = row[self._column]
            elif f:
                answer[self._column] += row[self._column]

        yield answer



# Joiners

def get_keys(keys: tp.Sequence[str], row: TRow) -> tp.Sequence[str]:
    return [key for key in row.keys() if key not in keys]


def join(keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b:TRowsIterable, is_left_clear,
         is_right_clear, a_suffix: str, b_suffix: str) -> TRowsGenerator:
    f1 = False
    f2 = False
    intersection = set()
    list_b = list(rows_b) if rows_b else []

    for a in rows_a:
        for b in list_b:
            if not f1:
                f1 = True
                intersection = set((key for key in a.keys() if key not in keys)).intersection(set(b.keys()))
            result = a.copy()
            for key in intersection:
                del result[key]
                result[key + a_suffix] = a[key]
                if not f2:
                    b[key + b_suffix] = b[key]
                    del b[key]

            result.update(b)
            yield result
        f2 = True
        if not f1 and is_left_clear:
            yield a
            break
    if not f2 and is_right_clear:
        for temp in list_b:
            yield temp
    if not f1 and is_left_clear:
        for temp in rows_a:
            yield temp

class InnerJoiner(Joiner):
    """Join with inner strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        for temp in join(keys, rows_a, rows_b,False,False, self._a_suffix, self._b_suffix):
            yield temp


class OuterJoiner(Joiner):
    """Join with outer strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        for temp in join(keys, rows_a, rows_b,True, True, self._a_suffix, self._b_suffix):
            yield temp


class LeftJoiner(Joiner):
    """Join with left strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        for temp in join(keys, rows_a, rows_b,True, False, self._a_suffix, self._b_suffix):
            yield temp


class RightJoiner(Joiner):
    """Join with right strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        for temp in join(keys, rows_a, rows_b,False,True, self._a_suffix, self._b_suffix):
            yield temp
