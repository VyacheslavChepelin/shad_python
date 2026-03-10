def merge_iterative(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    answer = []
    pointerA = 0
    pointerB = 0
    while pointerA < len(lst_a) or pointerB < len(lst_b):
        if pointerA >= len(lst_a):
            answer.append(lst_b[pointerB])
            pointerB += 1
        elif pointerB >= len(lst_b):
            answer.append(lst_a[pointerA])
            pointerA += 1
        elif lst_a[pointerA] < lst_b[pointerB]: #pls
            answer.append(lst_a[pointerA])
            pointerA += 1
        else:
            answer.append(lst_b[pointerB])
            pointerB += 1
    return answer


def merge_sorted(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list using `sorted`
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    return sorted(lst_a + lst_b)
