from django.utils.text import Truncator
from pydantic import AnyHttpUrl, BaseModel


class ProcessedMixImage(BaseModel):
    url: AnyHttpUrl
    valid: bool
    filename: str = None
    errors: list[str] = []

    @property
    def name(self) -> str:
        if not self.filename:
            return 'image'
        return self.filename if len(self.filename) < 50 else Truncator(self.name).chars(50)

    @property
    def error_message(self) -> str:
        return ', '.join(self.errors)

    def add_error_message(self, message: str):
        self.errors.append(message)
