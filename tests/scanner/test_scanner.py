import pytest
from playwright.sync_api import Page
from pages.page_objects.amazon_client import Amazon
from pages.page_objects.minmaxdeals import MinMaxDeals
from utilities.google_sheet.GoogleSheet import GoogleSheet


@pytest.mark.scanner
class TestScanner:

    def test_Scanner(self, page: Page) -> None:

        # Declare used objects
        page.context.clear_cookies()

        # amz.search_by("816657023169")

        minMax = MinMaxDeals(page)
        minMax.run()

        print("Running test")