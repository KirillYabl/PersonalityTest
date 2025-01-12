from typing import ClassVar, TypedDict

from typing_extensions import Self

from core.types import JSON


class ErrorData(TypedDict):
    err_code: int
    details: JSON


class UniqueErrorCodeMeta(type):
    _used_err_codes = set()

    def __new__(cls, name, bases, dct) -> Self:
        err_code = dct.get("err_code", None)
        if err_code is not None:
            if err_code in cls._used_err_codes:
                raise ValueError(f"err_code {err_code} уже используется, уже заняты {cls._used_err_codes}.")
            if err_code < 1001 or err_code > 1999:
                raise ValueError(
                    f"err_code должен быть от 1001 до 1999, получено {err_code}, уже заняты {cls._used_err_codes}."
                )
            cls._used_err_codes.add(err_code)
        else:
            if name != "ServiceException":
                raise ValueError(f"Необходимо задать атрибут класса err_code, уже заняты {cls._used_err_codes}.")
        return super().__new__(cls, name, bases, dct)


class ServiceException(Exception, metaclass=UniqueErrorCodeMeta):
    err_code: ClassVar[int]
    """Обший exception для ошибок, произошедших в сервисах."""

    def __init__(self, *args, details: JSON) -> None:
        self.details = details
        super().__init__(*args)


class ServiceExceptionGroup(ExceptionGroup):
    """Исключительная группа для обработки ошибок 'service'."""

    def __init__(self, message: str, exceptions: list[ServiceException]) -> None:
        self._service_exceptions = []
        super().__init__(message, exceptions)

    def add_error(self, exc: ServiceException) -> None:
        self._service_exceptions.append(exc)

    def raise_if_not_empty(self) -> None:
        """Рейзить исключения.

        :raises ServiceExceptionGroup: Если есть ошибки.
        """
        if self._service_exceptions:
            raise ServiceExceptionGroup("Есть сервисные ошибки.", self._service_exceptions)

    def get_errors_data(self) -> list[ErrorData]:
        return [{"err_code": e.err_code, "details": e.details} for e in self.exceptions]
