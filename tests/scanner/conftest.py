import pytest
from playwright.sync_api import Page


@pytest.fixture(autouse=True)
def run_around_tests(page: Page, integration):
    """
    Before each and after each
    """
    # Code that will run before your test, for example:

    # Actual test
    pass
    yield
    pass
    # Code that will run after your test