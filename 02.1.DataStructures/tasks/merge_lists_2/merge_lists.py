import typing as tp
import heapq

def merge(seq: tp.Sequence[tp.Sequence[int]]) -> list[int]:
    """
    :param seq: sequence of sorted sequences
    :return: merged sorted list
    """
    heap = []
    pointers = [0] * len(seq)
    for pos in range(len(seq)):
        if len(seq[pos]) != 0:
            heapq.heappush(heap, (seq[pos][0], pos))

    answer = []
    while heap:
        val, pos = heapq.heappop(heap)
        answer.append(val)
        pointers[pos] += 1
        if pointers[pos] < len(seq[pos]):
            index = pointers[pos]
            heapq.heappush(heap, (seq[pos][index], pos))
    return answer
