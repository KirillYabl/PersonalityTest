from core.errors_base import ServiceException


class UserNotFoundByTgIdException(ServiceException):
    err_code = 1001

class QuizNotFoundByIdException(ServiceException):
    err_code = 1002

class QuizAttemptNotFoundException(ServiceException):
    err_code = 1003

class InvalidAnswersException(ServiceException):
    err_code = 1004