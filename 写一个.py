def binary_search(arr: list[int], target: int) -> int:
    """
    在升序排列的列表中执行二分查找。
    
    :param arr: 已按升序排列的列表
    :param target: 需要查找的目标值
    :return: 目标值的索引；若未找到则返回 -1
    """
    # 初始化搜索区间的左右边界
    left = 0
    right = len(arr) - 1

    # 当左边界小于等于右边界时，说明当前区间仍然有效
    while left <= right:
        # 计算中间索引，采用 left + (right - left) // 2 的形式
        # 虽在 Python 中不会发生整数溢出，但该写法是其他语言中的最佳实践
        mid = left + (right - left) // 2

        # 中间元素恰好等于目标值，查找成功，直接返回索引
        if arr[mid] == target:
            return mid
        
        # 中间元素小于目标值，说明目标值只可能存在于右半区间
        elif arr[mid] < target:
            left = mid + 1
        
        # 中间元素大于目标值，说明目标值只可能存在于左半区间
        else:
            right = mid - 1

    # 循环结束仍未匹配到目标值，说明目标值不在列表中
    return -1