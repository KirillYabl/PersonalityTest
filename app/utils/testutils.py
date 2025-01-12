from collections.abc import Callable

from polyfactory import Use
from typing_extensions import TypeVar

T = TypeVar("T")


class Sequence(Use):
    """
    Аналог последовательности из factory_boy.

    https://github.com/litestar-org/polyfactory/issues/593#issuecomment-2437993101

    Пример использования:
    ```
    email = Sequence[str](lambda n: f'company{n:04}@test.tld')
    ```
    """

    def __init__(self, func: Callable[[int], T]) -> None:
        super().__init__(self.next)
        self.count = 0
        self.func = func

    def next(self) -> T:
        self.count += 1
        return self.func(self.count)
