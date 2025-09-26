class NabronirovalException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(NabronirovalException):
    detail = "Объект не найден"


class UniqueViolationException(NabronirovalException):
    detail = "Конфликт"


class AllRoomsAreBookedException(NabronirovalException):
    detail = "На эти даты уже все номера забронированны"


class UserAlreadyExistsException(NabronirovalException):
    detail = "Такой пользователь уже есть"


class IncorrectDateException(NabronirovalException):
    detail = "Неверно указаны даты"

