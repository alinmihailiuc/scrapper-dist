from playwright.sync_api import Page
from playwright._impl._api_types import TimeoutError
from retry import retry
from pages.base import Base


class Amazon(Base):

    def __init__(self, page: Page):
        super(Amazon, self).__init__(page)
        self.page = page
        self.locator_deliver_to = "//div[@id='nav-global-location-slot']"
        self.locator_input_zipcode = "//input[@data-action='GLUXPostalInputAction']"
        self.locator_apply = "//span[@id='GLUXZipUpdate-announce']"
        self.locator_continue = "//div[@class='a-popover-footer']//input[@id='GLUXConfirmClose']"
        self.locator_search_products = "//div[@class='nav-search-field ']//input"
        self.locator_search_submit = "//input[@value='Go']"
        self.locator_first_product = "//div[@data-asin][@data-uuid]/*[not(.//span[@class='s-label-popover-hover'])]//parent::div[@data-asin][@data-uuid]"

    def navigate_to_amazon_com(self):
        self.page.goto("https://www.amazon.com")

    def change_zip_code(self, zipcode="82801"):
        self.page.click(self.locator_deliver_to)
        self.page.wait_for_selector(self.locator_input_zipcode)
        self.page.fill(self.locator_input_zipcode, zipcode)
        self.page.click(self.locator_apply)
        self.page.wait_for_selector(self.locator_continue)
        self.page.click(self.locator_continue)

    @retry(TimeoutError)
    def search_by(self, search_value):
        """
        search_value: Can be anything UPC, Keyword, ASIN etc.
        """
        self.click_on_element(self.locator_search_products)
        self.fill_on_element(self.locator_search_products, '')
        self.page.keyboard.type(search_value)
        self.page.keyboard.press('Enter')
        self.page.wait_for_selector(self.locator_first_product)
        self.page.click(self.locator_first_product)
