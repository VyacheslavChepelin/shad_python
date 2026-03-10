import typing as tp


def traverse_dictionary_immutable(
        dct: tp.Mapping[str, tp.Any],
        prefix: str = "") -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param prefix: prefix for key used for passing total path through recursion
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    answer = []
    for key, value in dct.items():
        if not isinstance(value, tp.Mapping):
            answer.append((prefix + key, value))
        else:
            answer.extend(traverse_dictionary_immutable(value, prefix + key + '.'))
    return answer

def traverse_dictionary_mutable(
        dct: tp.Mapping[str, tp.Any],
        result: list[tuple[str, int]],
        prefix: str = "") -> None:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param result: list with pairs: (full key from root to leaf joined by ".", value)
    :param prefix: prefix for key used for passing total path through recursion
    :return: None
    """
    for key, value in dct.items():
        if not isinstance(value, tp.Mapping):
            result.append((prefix + key, value))
        else:
            traverse_dictionary_mutable(value, result, prefix + key + ".")

def traverse_dictionary_iterative(
        dct: tp.Mapping[str, tp.Any]
        ) -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """

    current  = dct
    while True:
        flag = True
        for key, value in current.items():
            if isinstance(value, tp.Mapping):
                flag = False
        if flag:
            break
        new_current = {}
        for key, value in current.items():
            if isinstance(value, tp.Mapping):
                while isinstance(value, tp.Mapping) and len(value) == 1:
                    new_key = next(iter(value))
                    value = value[new_key]
                    key = key + "." + new_key
                if isinstance(value, tp.Mapping):
                    for new_key, new_value in value.items():
                        new_current[key + '.' + new_key] = new_value
                else:
                    new_current[key] = value
            else:
                new_current[key] = value
        current = new_current
    answer = []
    for key, value in current.items():
        answer.append((key, value))
    return answer

