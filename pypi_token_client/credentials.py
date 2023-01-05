from abc import ABC, abstractmethod
from dataclasses import dataclass
from getpass import getpass

import keyring

keyring_service_name = "pypi-token-automation"


@dataclass(frozen=True)
class PypiCredentials:
    username: str
    password: str


def prompt_for_credentials() -> PypiCredentials:
    username = input("pypi username: ")
    password = getpass("pypi password: ")
    return PypiCredentials(username, password)


def get_credentials_from_keyring(
    username: str | None = None,
) -> PypiCredentials | None:
    cred = keyring.get_credential(keyring_service_name, username)
    if cred:
        return PypiCredentials(cred.username, cred.password)
    return None


def save_credentials_to_keyring(credentials: PypiCredentials):
    keyring.set_password(
        keyring_service_name, credentials.username, credentials.password
    )


class CredentialsProvider(ABC):
    @abstractmethod
    def get_credentials(self, username: str | None = None) -> PypiCredentials:
        """
        Get credentials from the provider.
        """

    def re_request_invalid_credentials(
        self,
        credentials: PypiCredentials,
        username_valid: bool = False,
    ) -> PypiCredentials | None:
        """
        Re-request credentials because they were found to be invalid.

        Args:
            credentials: Credentials that turned out to be invalid.
            username_valid: If it's known that at least the username was valid,
                this can be set to true to only request a new password (e.g.
                from the user).

        Returns:
            A new set of credentials or `None` if the provider is unable to get
            any.
        """
        return None

    def hint_valid_credentials(self, credentials: PypiCredentials) -> None:
        """
        Notify the provider that credentials were valid.

        The provider may choose to do nothing with this information.
        """


class StaticCredentialsProvider(CredentialsProvider):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_credentials(self, username: str | None = None) -> PypiCredentials:
        if username is not None and username != self.username:
            raise ValueError(f"no credentials for username {username}")
        return PypiCredentials(self.username, self.password)

    @classmethod
    def from_pypi_credentials(
        cls, credentials: PypiCredentials
    ) -> "StaticCredentialsProvider":
        return cls(
            username=credentials.username, password=credentials.password
        )


class KeyringAndPromptCredentialsProvider(CredentialsProvider):
    def get_credentials(self, username: str | None = None) -> PypiCredentials:
        credentials = get_credentials_from_keyring()
        if credentials is None:
            credentials = prompt_for_credentials()
        return credentials

    def re_request_invalid_credentials(
        self,
        credentials: PypiCredentials,
        username_valid: bool = False,
    ) -> PypiCredentials | None:
        credentials = prompt_for_credentials()
        return credentials

    def hint_valid_credentials(self, credentials: PypiCredentials) -> None:
        if get_credentials_from_keyring(username=credentials.username):
            prompt = "overwrite invalid credentials in keyring (Y/n)? "
        else:
            prompt = "save credentials to keyring (Y/n)? "
        if input(prompt) == "Y":
            save_credentials_to_keyring(credentials)
