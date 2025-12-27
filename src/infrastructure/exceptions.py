class InfrastructureException(Exception):
    """Базовая инфраструктурная ошибка"""
    pass


class DatabaseConnectionException(InfrastructureException):
    """Ошибка подключения к БД - 500 ошибка"""
    pass


class EntityNotFoundException(InfrastructureException):
    """Сущность не найдена - 404 ошибка"""
    pass


class EntityAlreadyExistsException(InfrastructureException):
    """Сущность уже существует - 409 ошибка"""
    pass


class FieldException(InfrastructureException):
    """Поле не найдено - 400 ошибка"""
    pass


class PageNotFoundException(InfrastructureException):
    """Страница не найдена - 404 ошибка"""
    pass
