import numpy as np
import numpy.typing as npt


def nonzero_product(matrix: npt.NDArray[np.int_]) -> int | None:
    """
    Compute product of nonzero diagonal elements of matrix
    If all diagonal elements are zeros, then return None
    :param matrix: array,
    :return: product value or None
    """
    diagonal_elements = np.diag(matrix)
    if np.count_nonzero(diagonal_elements) == 0:
        return None
    diagonal_elements = diagonal_elements[diagonal_elements != 0]
    return np.prod(diagonal_elements, dtype=int)
