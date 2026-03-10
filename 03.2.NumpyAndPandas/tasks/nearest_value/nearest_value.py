import numpy as np
import numpy.typing as npt


def nearest_value(matrix: npt.NDArray[np.float64], value: float) -> float | None:
    """
    Find nearest value in matrix.
    If matrix is empty return None
    :param matrix: input matrix
    :param value: value to find
    :return: nearest value in matrix or None
    """
    new_matrix = matrix.flatten()
    if len(new_matrix) == 0:
        return None
    argmin = np.argmin(np.abs(new_matrix - value))
    return float(new_matrix[argmin])
