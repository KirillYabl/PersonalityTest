from core.errors_base import ServiceException


class UserNotFoundByTgIdException(ServiceException):
    err_code = 1001

class QuizNotFoundByIdException(ServiceException):
    err_code = 1002