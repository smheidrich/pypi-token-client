from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

user_data_dir = str(Path("~/.autopypitok/persist-chromium").expanduser())
max_login_attempts = 3


class UnexpectedPageError(Exception):
    pass


class UnexpectedContentError(Exception):
    pass


class LoginError(Exception):
    pass


class UsernameError(LoginError):
    pass


class PasswordError(LoginError):
    pass


class CreateTokenError(Exception):
    pass


class TokenNameError(Exception):
    pass


def expect_page(page, expected_url: str):
    if page.url != expected_url:
        raise UnexpectedPageError(
            f"ended up on unexpected page {page.url} (expected {expected_url})"
        )


@dataclass
class TokenScope:
    pass


@dataclass
class AllProjects(TokenScope):
    pass


@dataclass
class SingleProject(TokenScope):
    name: str


@dataclass
class TokenListEntry:
    name: str
    scope: TokenScope
    created: datetime
    last_used: datetime | None
