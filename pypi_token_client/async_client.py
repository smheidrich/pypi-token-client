from asyncio import Lock
from contextlib import asynccontextmanager
from functools import wraps
from traceback import print_exc
from typing import Sequence

from dateutil.parser import isoparse
from playwright.async_api import async_playwright

from .common import (
    AllProjects,
    PasswordError,
    SingleProject,
    TokenListEntry,
    TokenNameError,
    UnexpectedContentError,
    UnexpectedPageError,
    UsernameError,
    user_data_dir,
)
from .credentials import PypiCredentials
from .utils import one_or_none


def _expect_page(page, expected_url: str):
    if page.url != expected_url:
        raise UnexpectedPageError(
            f"ended up on unexpected page {page.url} (expected {expected_url})"
        )


@asynccontextmanager
async def async_pypi_token_client(
    credentials: PypiCredentials, headless: bool = False
):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir, headless=headless
        )
        pages = context.pages
        assert len(pages) == 1
        page = pages[0]
        yield AsyncPypiTokenClientSession(context, page, credentials, headless)
        # XXX after this point it freezes forever in this line:
        # File "/usr/lib/python3.10/asyncio/runners.py", line 48, in run
        #   loop.run_until_complete(loop.shutdown_asyncgens())


def _with_lock(meth):
    @wraps(meth)
    async def _with_lock(self, *args, **kwargs):
        async with self._lock:
            return await meth(self, *args, **kwargs)

    return _with_lock


class AsyncPypiTokenClientSession:
    def __init__(
        self,
        context,
        page,
        credentials: PypiCredentials,
        headless: bool = True,
    ):
        self.context = context
        self.page = page
        self.credentials = credentials
        self.headless = headless
        self._lock = Lock()

    async def _handle_login(self):
        if not self.page.url.startswith("https://pypi.org/account/login/"):
            print("no login required")
            return
        username_input = one_or_none(
            await self.page.locator("#username").all()
        )
        if not username_input:
            raise UnexpectedContentError(
                "username field not found on login page"
            )
        password_input = one_or_none(
            await self.page.locator("#password").all()
        )
        if not password_input:
            raise UnexpectedContentError(
                "password field not found on login page"
            )
        await username_input.fill(self.credentials.username)
        await password_input.fill(self.credentials.password)
        async with self.page.expect_event(
            "domcontentloaded"
        ), self.page.expect_navigation():
            print("logging in...")
            await password_input.press("Enter")
        if self.page.url.startswith("https://pypi.org/account/login/"):
            username_errors_or_none = one_or_none(
                await self.page.locator("#username-errors ul li").all()
            )
            username_error = (
                await username_errors_or_none.inner_text()
                if username_errors_or_none is not None
                else None
            )
            if username_error is not None:
                raise UsernameError(username_error)
            password_errors_or_none = one_or_none(
                await self.page.locator("#password-errors ul li").all()
            )
            password_error = (
                await password_errors_or_none.inner_text()
                if password_errors_or_none is not None
                else None
            )
            if password_error is not None:
                raise PasswordError(password_error)
        return self.credentials

    async def _confirm_password(self):
        confirm_heading = one_or_none(
            await self.page.get_by_text("Confirm password to continue").all()
        )
        if not confirm_heading:
            print("no password confirmation required")
            return
        password_input = one_or_none(
            await self.page.locator("#password").all()
        )
        if not password_input:
            raise UnexpectedContentError("no password field found")
            return
        await password_input.fill(self.credentials.password)
        async with self.page.expect_event(
            "domcontentloaded"
        ), self.page.expect_navigation():
            print("confirming password...")
            await password_input.press("Enter")

    @asynccontextmanager
    async def _handle_errors(self):
        try:
            yield
        except Exception:
            print_exc()
            if self.headless:
                print(
                    "If you want to see what exactly went wrong in the "
                    "browser window, rerun with --headful"
                )
            else:
                print_exc()
                print(
                    "check browser window for what exactly went wrong "
                    "and close it once done"
                )
                await self.context.wait_for_event("close", timeout=0)

    @_with_lock
    async def create_project_token(
        self,
        project_name: str,
        token_name: str,
    ) -> str:
        await self.page.goto(
            "https://pypi.org/manage/account/token/",
            wait_until="domcontentloaded",
        )
        async with self._handle_errors():
            # login if necessary
            await self._handle_login()
            # confirm password if necessary
            await self._confirm_password()
            # fill in token name field
            token_name_input = one_or_none(
                await self.page.locator("#description").all()
            )
            if token_name_input is None:
                raise UnexpectedContentError(
                    "no token name field found on page"
                )
            await token_name_input.fill(token_name)
            # select token scope => project only
            scope_selector = one_or_none(
                await self.page.locator("#token_scope").all()
            )
            if scope_selector is None:
                raise UnexpectedContentError("no scope selector found on page")
            await scope_selector.select_option(
                value=f"scope:project:{project_name}"
            )
            async with self.page.expect_event(
                "domcontentloaded"
            ), self.page.expect_navigation():
                print("creating token...")
                await token_name_input.press("Enter")
            token_name_errors_or_none = one_or_none(
                await self.page.locator("#token-name-errors ul li").all()
            )
            token_name_error = (
                await token_name_errors_or_none.inner_text()
                if token_name_errors_or_none is not None
                else None
            )
            if token_name_error is not None:
                raise TokenNameError(token_name_error)
            token_block = one_or_none(
                await self.page.locator("#provisioned-key > code").all()
            )
            if not token_block:
                raise UnexpectedContentError("no token block found on page")
            token = await token_block.inner_text()
            return token

    @_with_lock
    async def get_token_list(self) -> Sequence[TokenListEntry]:
        await self.page.goto(
            "https://pypi.org/manage/account/",
            wait_until="domcontentloaded",
        )
        async with self._handle_errors():
            # login if necessary
            await self._handle_login()
            # confirm password if necessary
            await self._confirm_password()
            # get list
            token_rows = await self.page.locator(
                "#api-tokens > table > tbody > tr"
            ).all()
            token_list = []
            for row in token_rows:
                cols = await row.locator("th,td").all()
                name = await cols[0].inner_text()
                scope_str = await cols[1].inner_text()
                scope = (
                    AllProjects()
                    if scope_str == "All projects"
                    else SingleProject(scope_str)
                )
                created = isoparse(
                    await one_or_none(
                        await cols[2].locator("time").all()
                    ).get_attribute("datetime")
                )
                last_used_time_elem = one_or_none(
                    await cols[3].locator("time").all()
                )
                last_used = (
                    isoparse(
                        await last_used_time_elem.get_attribute("datetime")
                    )
                    if last_used_time_elem is not None
                    else None
                )
                entry = TokenListEntry(name, scope, created, last_used)
                token_list.append(entry)
            return token_list
