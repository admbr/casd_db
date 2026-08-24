from jinja2 import Environment, FileSystemLoader, select_autoescape
import smtplib
from collections.abc import Callable
from pydantic import BaseModel, Field, prop


class EmailFailure(BaseModel):
    apartment: str | None
    email: str | None
    reason: str


class EmailReport(BaseModel):
    sent: int = 0
    failed: list[EmailFailure] = Field(default_factory=list)

    @property
    def total(self) -> int:
        return self.sent + len(self.failed)

    @property
    def success_rate(self) -> float:
        return self.sent / self.total if self.total > 0 else 0.0


class NotifyService:
    pass
