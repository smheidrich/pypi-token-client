"""
Sync "client", which is just a bunch of wrapper functions around the async one.

NOTE that this is less flexible than the async client because you can't have
sessions that span multiple function invocations. I tried to support sessions
here too but to no avail:
https://gitlab.com/smheidrich/pypi-token-client/-/merge_requests/1
"""
import asyncio

from . import async_client
from .credentials import PypiCredentials


async def _create_project_token_async(
    project_name: str,
    token_name: str,
    credentials: PypiCredentials,
    headless: bool,
):
    async with async_client.async_pypi_token_client(
        credentials, headless
    ) as session:
        return await session.create_project_token(project_name, token_name)


def create_project_token(
    project: str,
    token_name: str,
    credentials: PypiCredentials,
    headless: bool = False,
):
    return asyncio.run(
        _create_project_token_async(
            project, token_name, credentials, headless=headless
        )
    )


async def _get_token_list_async(
    credentials: PypiCredentials,
    headless: bool,
):
    async with async_client.async_pypi_token_client(
        credentials, headless
    ) as session:
        return await session.get_token_list()


def get_token_list(credentials: PypiCredentials, headless: bool = False):
    return asyncio.run(_get_token_list_async(credentials, headless=headless))
