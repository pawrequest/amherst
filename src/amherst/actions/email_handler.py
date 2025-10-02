from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


# class EmailHandler(ABC):
#     """
#     Abstract class for handling emails
#     """
#
#     @abstractmethod
#     def send_email(self, email: Email) -> None:
#         ...


class EmailHandler(ABC):
    """
    Abstract class for handling emails
    """

    @abstractmethod
    def create_open_email(self, email: Email) -> None:
        ...


# @dataclass
# class Email:
#     """Dataclass representing an email"""
#     to_address: str
#     subject: str
#     body: str
#     attachment_path: Path or None = None
#
#     def send(self, sender: EmailHandler) -> None:
#         sender.send_email(self)


@dataclass
class Email:
    """Dataclass representing an email"""
    to_address: str
    subject: str
    body: str
    attachment_paths: list[Path] or None = None

    def __post_init__(self):
        if self.attachment_paths is None:
            self.attachment_paths = []

    def send(self, sender: EmailHandler) -> None:
        sender.create_open_email(self)


class EmailError(Exception):
    """
    Exception for email handling
    """
    ...
