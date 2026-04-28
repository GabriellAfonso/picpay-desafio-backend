from typing import Any


class DomainException(Exception):
    def __init__(self, message: Any, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
