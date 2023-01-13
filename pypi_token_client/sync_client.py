"""
Sync "client", which is just a bunch of wrapper functions around the async one.

TODO missing a lot of functionality, don't use yet.

NOTE that this is less flexible than the async client because you can't have
sessions that span multiple function invocations. I tried to support sessions
here too but to no avail:
https://gitlab.com/smheidrich/pypi-token-client/-/merge_requests/1
"""
import asyncio
from pathlib import Path

from pypi_token_client.common import TokenScope

from . import async_client
from .credentials import PypiCredentials


async def _create_token_async(
    token_name: str,
    scope: TokenScope,
    credentials: PypiCredentials,
    headless: bool,
    persist_to: Path | str | None,
):
    async with async_client.async_pypi_token_client(
        credentials, headless, persist_to
    ) as session:
        return await session.create_token(token_name, scope)


def create_token(
    token_name: str,
    scope: TokenScope,
    credentials: PypiCredentials,
    headless: bool = False,
    persist_to: Path | str | None = None,
):
    return asyncio.run(
        _create_token_async(
            token_name, scope, credentials, headless, persist_to
        )
    )


async def _get_token_list_async(
    credentials: PypiCredentials,
    headless: bool,
    persist_to: Path | str | None,
):
    async with async_client.async_pypi_token_client(
        credentials, headless, persist_to
    ) as session:
        return await session.get_token_list()


def get_token_list(
    credentials: PypiCredentials,
    headless: bool = False,
    persist_to: Path | str | None = None,
):
    return asyncio.run(
        _get_token_list_async(credentials, headless, persist_to)
    )
