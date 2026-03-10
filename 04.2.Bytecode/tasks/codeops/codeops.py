import dis
import types


def count_recur(operations):
    cur_dict = {}
    for operation in operations:
        if operation.opname not in cur_dict:
            cur_dict[operation.opname] = 0
        cur_dict[operation.opname] += 1
        if isinstance(operation.argval, types.CodeType):
            temp_dict = count_recur(dis.get_instructions(operation.argval))
            if len(temp_dict) > 0:
                for k, v in temp_dict.items():
                    if k not in cur_dict:
                        cur_dict[k] = 0
                    cur_dict[k] += v
    return cur_dict



def count_operations(source_code: types.CodeType) -> dict[str, int]:
    """Count byte code operations in given source code.

    :param source_code: the bytecode operation names to be extracted from
    :return: operation counts
    """

    return count_recur(dis.get_instructions(source_code))
