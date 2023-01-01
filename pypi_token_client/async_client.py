from contextlib import asynccontextmanager
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


def expect_page(page, expected_url: str):
    if page.url != expected_url:
        raise UnexpectedPageError(
            f"ended up on unexpected page {page.url} (expected {expected_url})"
        )


async def handle_login(
    context, page, credentials: PypiCredentials
) -> PypiCredentials:
    if not page.url.startswith("https://pypi.org/account/login/"):
        print("no login required")
        return
    username_input = one_or_none(await page.locator("#username").all())
    if not username_input:
        raise UnexpectedContentError("username field not found on login page")
    password_input = one_or_none(await page.locator("#password").all())
    if not password_input:
        raise UnexpectedContentError("password field not found on login page")
    await username_input.fill(credentials.username)
    await password_input.fill(credentials.password)
    async with page.expect_event("domcontentloaded"), page.expect_navigation():
        print("logging in...")
        await password_input.press("Enter")
    if page.url.startswith("https://pypi.org/account/login/"):
        username_errors_or_none = one_or_none(
            await page.locator("#username-errors ul li").all()
        )
        username_error = (
            await username_errors_or_none.inner_text()
            if username_errors_or_none is not None
            else None
        )
        if username_error is not None:
            raise UsernameError(username_error)
        password_errors_or_none = one_or_none(
            await page.locator("#password-errors ul li").all()
        )
        password_error = (
            await password_errors_or_none.inner_text()
            if password_errors_or_none is not None
            else None
        )
        if password_error is not None:
            raise PasswordError(password_error)
    return credentials


async def confirm_password(context, page, credentials: PypiCredentials):
    confirm_heading = one_or_none(
        await page.get_by_text("Confirm password to continue").all()
    )
    if not confirm_heading:
        print("no password confirmation required")
        return
    password_input = one_or_none(await page.locator("#password").all())
    if not password_input:
        raise UnexpectedContentError("no password field found")
        return
    await password_input.fill(credentials.password)
    async with page.expect_event("domcontentloaded"), page.expect_navigation():
        print("confirming password...")
        await password_input.press("Enter")


@asynccontextmanager
async def context_page_persistent(
    url: str, headless: bool = True, check_url: bool = False
):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir, headless=headless
        )
        pages = context.pages
        assert len(pages) == 1
        page = pages[0]
        await page.goto(url, wait_until="domcontentloaded")
        if check_url:
            expect_page(page, url)
        yield context, page


async def list_projects():
    async with context_page_persistent(
        "https://pypi.org/manage/projects/"
    ) as (context, page):
        project_titles = [
            x.split()[0]
            for x in await page.locator(
                ".package-snippet__title"
            ).all_inner_texts()
        ]
        print("\n".join(project_titles))


@asynccontextmanager
async def handle_errors(context, headless: bool):
    try:
        yield
    except Exception:
        print_exc()
        if headless:
            print(
                "If you want to see what exactly went wrong in the browser "
                "window, rerun with --headful"
            )
        else:
            print_exc()
            print(
                "check browser window for what exactly went wrong "
                "and close it once done"
            )
            await context.wait_for_event("close", timeout=0)


async def login(
    credentials: PypiCredentials, headless: bool = True
) -> Sequence[TokenListEntry]:
    async with context_page_persistent(
        "https://pypi.org/manage/account/", headless=headless
    ) as (context, page):
        async with handle_errors(context, headless):
            await handle_login(context, page, credentials)


async def create_project_token(
    project_name: str,
    token_name: str,
    credentials: PypiCredentials,
    headless: bool = True,
) -> str:
    async with context_page_persistent(
        "https://pypi.org/manage/account/token/", headless=headless
    ) as (context, page):
        async with handle_errors(context, headless):
            # login if necessary
            await handle_login(context, page, credentials)
            # confirm password if necessary
            await confirm_password(context, page, credentials)
            # fill in token name field
            token_name_input = one_or_none(
                await page.locator("#description").all()
            )
            if token_name_input is None:
                raise UnexpectedContentError(
                    "no token name field found on page"
                )
            await token_name_input.fill(token_name)
            # select token scope => project only
            scope_selector = one_or_none(
                await page.locator("#token_scope").all()
            )
            if scope_selector is None:
                raise UnexpectedContentError("no scope selector found on page")
            await scope_selector.select_option(
                value=f"scope:project:{project_name}"
            )
            async with page.expect_event(
                "domcontentloaded"
            ), page.expect_navigation():
                print("creating token...")
                await token_name_input.press("Enter")
            token_name_errors_or_none = one_or_none(
                await page.locator("#token-name-errors ul li").all()
            )
            token_name_error = (
                await token_name_errors_or_none.inner_text()
                if token_name_errors_or_none is not None
                else None
            )
            if token_name_error is not None:
                raise TokenNameError(token_name_error)
            token_block = one_or_none(
                await page.locator("#provisioned-key > code").all()
            )
            if not token_block:
                raise UnexpectedContentError("no token block found on page")
            token = await token_block.inner_text()
            return token


async def get_token_list(
    credentials: PypiCredentials, headless: bool = True
) -> Sequence[TokenListEntry]:
    async with context_page_persistent(
        "https://pypi.org/manage/account/", headless=headless
    ) as (context, page):
        async with handle_errors(context, headless):
            # login if necessary
            await handle_login(context, page, credentials)
            # confirm password if necessary
            await confirm_password(context, page, credentials)
            # get list
            token_rows = await page.locator(
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
