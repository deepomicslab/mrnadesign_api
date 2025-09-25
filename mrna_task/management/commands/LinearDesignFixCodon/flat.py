# flat.py

from typing import TypeVar, Generic, Callable, List, Iterator, Optional
from base import LINEAR_DESIGN_CACHELINE

K = TypeVar('K')  # 键的类型
T = TypeVar('T')  # 值的类型


class DefaultIndex(Generic[K]):
    """
    默认的索引函数，将键转换为整数索引。
    假设键可以直接转换为整数。
    """

    def __call__(self, key: K) -> int:
        return int(key)


class Flat(Generic[K, T]):
    """
    一个平坦的存储容器，使用索引函数将键映射到值。

    参数:
    - Key: 键的类型。
    - T: 值的类型。
    - IndexFn: 一个将键映射到整数索引的可调用对象。
    """

    def __init__(self, index_fn: Callable[[K], int] = DefaultIndex()):
        self.index_fn: Callable[[K], int] = index_fn
        self.data: List[Optional[T]] = []

    def __iter__(self) -> Iterator[T]:
        """
        返回存储值的迭代器。
        """
        return iter(self.data)

    def empty(self) -> bool:
        """
        始终返回False，模仿C++中的empty()方法。
        """
        return False

    def reserve(self, n: int):
        """
        预分配n个元素的空间。
        在Python中，列表是动态的，但此方法可以通过添加None来扩展列表。
        """
        if len(self.data) < n:
            self.data.extend([None] * (n - len(self.data)))

    def resize(self, n: int):
        """
        调整存储的大小以容纳n个元素。
        如果n大于当前大小，则用None扩展列表。
        如果n小于当前大小，则截断列表。
        """
        current_size = len(self.data)
        if n < current_size:
            self.data = self.data[:n]
        elif n > current_size:
            self.data.extend([None] * (n - current_size))

    def __getitem__(self, key):
        """
        通过键或索引获取项。
        如果键是整数并且使用的是默认的IndexFn，它将键视为索引。
        否则，使用索引函数将键映射到索引。
        """
        if isinstance(key, int):
            if isinstance(self.index_fn, DefaultIndex):
                # 使用DefaultIndex时，键被视为索引
                return self.data[key]
            else:
                # 如果IndexFn不是DefaultIndex，假设键是索引
                return self.data[key]
        else:
            # 使用索引函数将键映射到索引
            index = self.index_fn(key)
            return self.data[index]

    def __setitem__(self, key, value: T):
        """
        通过键或索引设置项。
        如果键是整数并且使用的是默认的IndexFn，它将键视为索引。
        否则，使用索引函数将键映射到索引。
        """
        if isinstance(key, int):
            if isinstance(self.index_fn, DefaultIndex):
                # 使用DefaultIndex时，键被视为索引
                self.data[key] = value
            else:
                # 如果IndexFn不是DefaultIndex，假设键是索引
                self.data[key] = value
        else:
            # 使用索引函数将键映射到索引
            index = self.index_fn(key)
            self.data[index] = value

    def size(self) -> int:
        """
        返回存储中元素的数量。
        """
        return len(self.data)
