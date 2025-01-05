from abc import ABC, abstractmethod

import uvloop
import click
from loguru import logger

class Command(ABC):
    """
    Класс команды, умеет делать прямой прогон, обратный (если это воозможно) и содержит интерфейс запуска через командную строку.
    
    Для запуска через командную строку нужно использовать -m флаг в python, например

    ```
    python -m commands.my_command
    ИЛИ
    python -m commands.my_command --unrun # обратный прогон
    ИЛИ
    uv run -m commands.my_command
    ```
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Если в команду нужно передать параметры, то они передаются при инициализации.

        Поэтому у прямйо и обратной команды должны быть одинаковые параметры
        """
        self.args = args
        self.kwargs = kwargs
        logger.debug(f"{self.__class__.__name__} запущен с {args=} и {kwargs=}")

    @abstractmethod
    async def run(self) -> None:
        """Прямой запуск команды."""

    @abstractmethod
    async def unrun(self) -> None:
        """Обратный запуск команды."""

    def run_cli(self) -> None:
        """Запуск через командную строку."""

        @click.command()
        @click.option("--unrun", is_flag=True, default=False, help="Back mode")
        def cli(unrun: bool) -> None:
            logger.debug(f"{self.__class__.__name__} {unrun=}")
            if unrun:
                uvloop.run(self.unrun())
            else:
                uvloop.run(self.run())

        cli()
