class AppError(Exception):
    status_code: int = 400

    def __init__(self, message: str = "Ошибка приложения") -> None:
        super().__init__(message)
        self.message = message


class AuthenticationError(AppError):
    status_code = 401

    def __init__(self, message: str = "Требуется авторизация") -> None:
        super().__init__(message)


class AuthorizationError(AppError):
    status_code = 403

    def __init__(self, message: str = "Недостаточно прав") -> None:
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404

    def __init__(self, message: str = "Объект не найден") -> None:
        super().__init__(message)


class ConflictError(AppError):
    status_code = 409

    def __init__(self, message: str = "Конфликт данных") -> None:
        super().__init__(message)


class InternalServerError(AppError):
    status_code = 500

    def __init__(self, message: str = "Внутренняя ошибка сервера") -> None:
        super().__init__(message)
