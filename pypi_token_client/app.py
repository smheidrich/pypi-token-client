from datetime import date
from functools import wraps
from pprint import pprint

from . import sync_client
from .common import LoginError
from .credentials import (
    PypiCredentials,
    get_credentials_from_keyring,
    prompt_for_credentials,
    save_credentials_to_keyring,
)

max_login_attempts = 3


def prompt_credentials_on_login_fail(f, /):
    @wraps(f)
    def _prompt_credentials_on_login_fail(*args, **kwargs):
        credentials = get_credentials_from_keyring()
        if not credentials:
            credentials = prompt_for_credentials()
        last_exc = Exception()  # dummy
        for _ in range(max_login_attempts):
            try:
                f(*args, credentials=credentials, **kwargs)
                # TODO this sucks because other exceptions prevent saving
                # creds... better would be to get a signal back that login
                # succeeded
                save_credentials_to_keyring(credentials)
                break
            except LoginError as e:
                print(f"Login failed: {e}")
                last_exc = e
                credentials = prompt_for_credentials()
        else:
            print("Giving up.")
            raise last_exc from last_exc

    return _prompt_credentials_on_login_fail


@prompt_credentials_on_login_fail
def create_token(
    credentials: PypiCredentials,
    project: str,
    token_name: str | None = None,
    headless: bool = True,
):
    token_name = token_name or f"a{date.today()}"
    with sync_client.sync_pypi_token_client(credentials, headless) as session:
        token = session.create_project_token(project, token_name)
    print("Created token:")
    print(token)


@prompt_credentials_on_login_fail
def list_tokens(credentials: PypiCredentials, headless: bool = True):
    with sync_client.sync_pypi_token_client(credentials, headless) as session:
        tokens = session.get_token_list(credentials, headless)
    pprint(tokens)
