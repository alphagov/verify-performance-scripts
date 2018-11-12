import pytest
from unittest.mock import MagicMock

from performance.config import TestConfig


@pytest.fixture
def config():
    """A fixture for test configuration."""
    return TestConfig()


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    # Example similar to
    # https://docs.pytest.org/en/latest/monkeypatch.html#example-preventing-requests-from-remote-operations

    # The following are set up only to ensure that external requests cannot be made without causing a fatal error; it is
    # still up to each test to ensure it has the mocks or fixtures available that it requires.
    no_connection_exception = ConnectionError('HTTP connection not allowed in test.')
    monkeypatch.setattr("requests.sessions.Session.request", MagicMock(side_effect=no_connection_exception))
    monkeypatch.setattr("httplib2.Http", MagicMock(side_effect=no_connection_exception))
