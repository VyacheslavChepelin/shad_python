import numpy as np
import numpy.typing as npt


def max_element(array: npt.NDArray[np.int_]) -> int | None:
    """
    Return max element before zero for input array.
    If appropriate elements are absent, then return None
    :param array: array,
    :return: max element value or None
    """
    indices = np.where(array == 0)[0]
    indices = indices[indices < (len(array) - 1)]
    if len(indices) == 0:
       return None
    return int(np.max(array[indices + 1]))
