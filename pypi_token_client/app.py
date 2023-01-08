import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from itertools import count
from pathlib import Path
from pprint import pprint

from .async_client import AsyncPypiTokenClientSession, async_pypi_token_client
from .common import PasswordError, UsernameError
from .credentials import (
    get_credentials_from_keyring_and_prompt,
    prompt_for_credentials,
    save_credentials_to_keyring,
)

max_login_attempts = 3


@asynccontextmanager
async def logged_in_session(
    username: str | None,
    password: str | None,
    headless: bool,
    persist_to: Path | None,
) -> AsyncIterator[AsyncPypiTokenClientSession]:
    # don't do anything interactive (e.g. ask about saving to keyring or retry
    # with prompt) if both username and password are provided (generally
    # suggests no interactivity is desired)
    interactive = username is None or password is None
    credentials, credentials_are_new = get_credentials_from_keyring_and_prompt(
        username, password
    )
    async with async_pypi_token_client(
        credentials, headless, persist_to
    ) as session:
        for attempt in count():
            try:
                did_login = await session.login()
                if did_login and credentials_are_new and interactive:
                    save = input(
                        "success! save credentials to keyring (Y/n)? "
                    )
                    if save == "Y":
                        save_credentials_to_keyring(credentials)
                        print("saved")
                    else:
                        print("not saving")
                break
            except (UsernameError, PasswordError) as e:
                print(f"Login failed: {e}")
                if attempt >= max_login_attempts or not interactive:
                    print("Giving up.")
                    raise
                credentials = prompt_for_credentials()
                credentials_are_new = True
                session.credentials = credentials
        yield session


def create_token(
    project: str,
    token_name: str | None = None,
    headless: bool = True,
    persist_to: Path | None = None,
    username: str | None = None,
    password: str | None = None,
) -> None:
    async def _run():
        token_name_ = token_name or f"a{date.today()}"
        async with logged_in_session(
            username, password, headless, persist_to
        ) as session:
            token = await session.create_project_token(project, token_name_)
        print("Created token:")
        print(token)

    asyncio.run(_run())


def list_tokens(
    headless: bool = True,
    persist_to: Path | None = None,
    username: str | None = None,
    password: str | None = None,
) -> None:
    async def _run():
        async with logged_in_session(
            username, password, headless, persist_to
        ) as session:
            tokens = await session.get_token_list()
        pprint(tokens)

    asyncio.run(_run())


def delete_token(
    name: str,
    headless: bool = True,
    persist_to: Path | None = None,
    username: str | None = None,
    password: str | None = None,
) -> None:
    async def _run():
        async with logged_in_session(
            username, password, headless, persist_to
        ) as session:
            await session.delete_token(name)

    asyncio.run(_run())
