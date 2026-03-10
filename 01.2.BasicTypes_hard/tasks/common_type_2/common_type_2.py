import typing as tp

priority = [str, bool, int, float, complex]

def is_valid_type(cur: tp.Any) -> bool:
    return not (cur is None or cur == '')

def is_convertable_to_bool_type(cur: tp.Any) -> bool:
    return cur is None or cur == "" or (cur is bool) or cur == 1 or cur == 0

def convert_to_common_type(data: list[tp.Any]) -> list[tp.Any]:
    """
    Takes list of multiple types' elements and convert each element to common type according to given rules
    :param data: list of multiple types' elements
    :return: list with elements converted to common type
    """
    has_list = False
    for element in data:
        if (type(element) is list) or (type(element) is tuple):
            has_list = True

    if has_list:
        answer = []
        for element in data:
            if not is_valid_type(element):
                answer.append([])
            elif type(element) in priority:
                answer.append([element])
            else:
                answer.append(list(element))
        return answer
    else:
        max_priority = 0
        for element in data:
            if is_valid_type(element):
                max_priority = max(max_priority, priority.index(type(element)))

        data_type = priority[max_priority]
        if max_priority == 2: # костыль
            can_convert_to_bool = True
            for element in data:
                if not is_convertable_to_bool_type(element):
                    can_convert_to_bool = False
                    break
            if can_convert_to_bool:
                return [bool(element) for element in data]

        return [data_type() if not is_valid_type(element) else  data_type(element) for element in data]
