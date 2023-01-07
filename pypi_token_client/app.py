import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from itertools import count
from pathlib import Path
from pprint import pprint

from .async_client import AsyncPypiTokenClientSession, async_pypi_token_client
from .common import LoginError
from .credentials import (
    PypiCredentials,
    get_credentials_from_keyring,
    prompt_for_credentials,
    save_credentials_to_keyring,
)

max_login_attempts = 3


@asynccontextmanager
async def logged_in_session(
    credentials: PypiCredentials | None,
    headless: bool,
    persist_to: Path | None,
) -> AsyncIterator[AsyncPypiTokenClientSession]:
    credentials_are_new = False
    if credentials is None:
        credentials = get_credentials_from_keyring()
    if credentials is None:
        credentials = prompt_for_credentials()
        credentials_are_new = True
    async with async_pypi_token_client(
        credentials, headless, persist_to
    ) as session:
        for attempt in count():
            try:
                did_login = await session.login()
                if did_login and credentials_are_new:
                    save = input(
                        "success! save credentials to keyring (Y/n)? "
                    )
                    if save == "Y":
                        save_credentials_to_keyring(credentials)
                        print("saved")
                    else:
                        print("not saving")
                break
            except LoginError as e:
                print(f"Login failed: {e}")
                if attempt >= max_login_attempts:
                    print("Giving up.")
                    raise
                credentials = prompt_for_credentials()
                credentials_are_new = True
        yield session


def create_token(
    project: str,
    token_name: str | None = None,
    headless: bool = True,
    persist_to: Path | None = None,
    credentials: PypiCredentials | None = None,
) -> None:
    async def _run():
        token_name_ = token_name or f"a{date.today()}"
        async with logged_in_session(
            credentials, headless, persist_to
        ) as session:
            token = await session.create_project_token(project, token_name_)
        print("Created token:")
        print(token)

    asyncio.run(_run())


def list_tokens(
    headless: bool = True,
    persist_to: Path | None = None,
    credentials: PypiCredentials | None = None,
) -> None:
    async def _run():
        async with logged_in_session(
            credentials, headless, persist_to
        ) as session:
            tokens = await session.get_token_list()
        pprint(tokens)

    asyncio.run(_run())
