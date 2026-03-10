def get_common_type(type1: type, type2: type) -> type:
    """
    Calculate common type according to rule, that it must have the most adequate interpretation after conversion.
    Look in tests for adequacy calibration.
    :param type1: one of [bool, int, float, complex, list, range, tuple, str] types
    :param type2: one of [bool, int, float, complex, list, range, tuple, str] types
    :return: the most concrete common type, which can be used to convert both input values
    """
    types = [bool, int, float, complex, list, range, tuple, str]
    index1 = 0
    index2 = 0
    for i in range(len(types)):
        if types[i] == type1:
            index1 = i
        if types[i] == type2:
            index2 = i
    table = [
        [bool,  int, float, complex, str, str, str, str],
        [int,   int, float, complex, str, str, str, str],
        [float, float, float, complex, str, str, str, str],
        [complex, complex, complex, complex, str, str, str, str],
        [str, str, str, str, list, list, list, str],
        [str, str, str, str, list, tuple, tuple, str],
        [str, str, str, str, list, tuple, tuple, str],
        [str, str, str, str, str, str, str, str]
    ]
    return table[index1][index2]
