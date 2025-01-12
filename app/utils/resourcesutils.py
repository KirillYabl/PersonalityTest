from collections.abc import Hashable
from functools import lru_cache


class EnumValuesMixin:
    @classmethod
    @lru_cache(maxsize=1)
    def values(cls) -> set[Hashable]:
        return {item.value for item in cls}
