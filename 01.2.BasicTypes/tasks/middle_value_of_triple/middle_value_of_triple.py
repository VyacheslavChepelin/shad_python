def get_middle_value(a: int, b: int, c: int) -> int:
    """
    Takes three values and returns middle value.
    """
    first_compare = a < b
    second_compare = b < c
    if(first_compare == second_compare):
        return b
    third_compare = a < c
    if(third_compare ^ second_compare): #pls
        return c
    return a
