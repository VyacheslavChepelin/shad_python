from cmath import isnan

import numpy as np
import numpy.typing as npt


def replace_nans(matrix: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    Replace all nans in matrix with average of other values.
    If all values are nans, then return zero matrix of the same size.
    :param matrix: matrix,
    :return: replaced matrix
    """
    my_matrix = matrix.copy()
    temp = np.nanmean(my_matrix)
    my_matrix[np.isnan(my_matrix)] =  temp if not isnan(temp) else 0
    return my_matrix
