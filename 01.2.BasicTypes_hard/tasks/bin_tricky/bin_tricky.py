from collections.abc import Sequence


def find_median(nums1: Sequence[int], nums2: Sequence[int]) -> float:
    """
    Find median of two sorted sequences. At least one of sequences should be not empty.
    :param nums1: sorted sequence of integers
    :param nums2: sorted sequence of integers
    :return: middle value if sum of sequences' lengths is odd
             average of two middle values if sum of sequences' lengths is even
    """
    n = len(nums1)
    m = len(nums2)
    total = n + m
    if n > m:
        return find_median(nums2, nums1)
    if n == 0:
        return (nums2[(total - 1) // 2] + nums2[total // 2]) / 2

    left = 0
    right = n + 1
    in_left_size = (n + m + 1) // 2
    while right - left > 1:
        mid = (left + right) // 2
        index = in_left_size - mid
        if mid != 0 and nums1[mid - 1] > nums2[index]:
            right = mid
        elif mid != n and nums1[mid] < nums2[index - 1]:
            left = mid
        else:
            left = mid

    left_border  = []
    right_border = []
    index = in_left_size - left
    if left != 0:
        left_border.append(nums1[left - 1])
    if index != 0:
        left_border.append(nums2[index - 1])

    if left != n:
        right_border.append(nums1[left])
    if index != m:
        right_border.append(nums2[index])


    if total % 2 == 0:
        return (max(left_border) + min(right_border)) / 2
    else:
        return float(max(left_border))

