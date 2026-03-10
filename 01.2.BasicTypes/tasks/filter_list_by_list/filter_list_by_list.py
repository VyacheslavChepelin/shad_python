def filter_list_by_list(lst_a: list[int] | range, lst_b: list[int] | range) -> list[int]:
    """
    Filter first sorted list by other sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: filtered sorted list
    """
    answer = []
    pointerA = 0
    pointerB = 0
    while pointerA < len(lst_a):
        if pointerB >= len(lst_b):
            answer.append(lst_a[pointerA])
            pointerA += 1
        elif lst_a[pointerA] == lst_b[pointerB]:
            pointerA += 1
        elif lst_a[pointerA] < lst_b[pointerB]: #pls
            answer.append(lst_a[pointerA])
            pointerA += 1
        else:
            pointerB += 1
    return answer
