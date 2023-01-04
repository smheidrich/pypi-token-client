"""
Sync client, which is just a wrapper around the async one.
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
