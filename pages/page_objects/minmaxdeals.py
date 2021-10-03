from playwright.sync_api import Page
import re
from pages.base import Base
from utilities.support.file_handler.file_handler import generate_csv
from retry import retry
from playwright._impl._api_types import Error as playwright_error
from utilities.google_sheet.GoogleSheet import GoogleSheet


class MinMaxDeals(Base):
    def __init__(self, page: Page):
        super(MinMaxDeals, self).__init__(page)
        self.url = "https://minmaxdeals.com/"
        self.googleSheet = GoogleSheet("1A0jSDwG1MdIOfY41EqFpcXgAveEyFTZxfkzb8r0kzv4")
        self.update_upc_cost = []
        self.current_product = None
        self.csv_name = "minmaxdeals.csv"
        self.page = page
        self.locator_shop = "//a[@href='/collections/in-stock']"
        self.locator_product = "//div[@class='grid-view-item product-card']"
        self.locator_product_UPC = "//div[@class='scrollable-wrapper']//strong[not(contains(text(),'B'))][not(contains(text(),'$'))][not(contains(text(),'units'))][not(contains(text(),'weeks'))][not(contains(text(),'month'))][not(contains(text(),'day'))][not(contains(text(),'stock'))]"
        self.locator_product_ASIN = "//div[@class='scrollable-wrapper']//strong[contains(text(),'B')]"
        self.locator_product_price = "//div[@id='shopify-section-product-template']//div[@class='price__regular']//span[@class='price-item price-item--regular']"
        self.locator_popup_close = "//button[@title='Close']"
        self.locator_page_text = "//li[@class='pagination__text']"
        self.locator_page_next = "//a[contains(@href,'/collections/in-stock?page')]"


    def check_popup(self):
        if self.check_if_element_exists(self.locator_popup_close):
            pop_ups = self.page.query_selector_all(self.locator_popup_close)
            for pop_up in pop_ups:
                if pop_up.is_visible():
                    print("Close popup")
                    try:
                        pop_up.click()
                    except:
                        pass

    def reached_page_max(self):
        self.page.wait_for_selector(self.locator_page_text)
        pages = self.page.text_content(self.locator_page_text).strip().replace(" ", "").replace("Page", "")
        current_page, max_page = pages.split("of")
        return current_page == max_page

    def navigate(self):
        self.page.goto(self.url)
        self.check_popup()

    def go_to_shop(self):
        self.navigate()
        self.page.click(self.locator_shop)
        self.check_popup()

    def click_product_by_index(self, index):
        # index usually starts from 0, added 1 as xpath locators starts from 1
        self.page.click(self.get_element_locator_by_index(self.locator_product, index))
        self.check_popup()

    def run(self):
        self.go_to_shop()
        reach_page_max = self.reached_page_max()
        while not reach_page_max:
            # Iterate products
            self.iterate_products()

            # Next page
            self.page.click(self.locator_page_next)

            # Refresh condition
            reach_page_max = self.reached_page_max()
        self.iterate_products()
        if len(self.update_upc_cost) > 0:
            generate_csv(self.csv_name, ['UPC', 'COST'], self.update_upc_cost)
            # TODO scan unlimited to be introduced
            # After scan is finished update GoogleSheet
            for values in self.update_upc_cost:
                self.googleSheet.update_sheet_with_values_at_the_end(values)

    @retry(playwright_error, tries=3, delay=3)
    def find_upc(self):
        regex_upc = "[0-9]{11,15}"
        return_upc = re.findall(regex_upc, self.page.inner_html("[class='smart-tabs-wrapper Rte']"))[0]
        return return_upc

    @retry()
    def get_upc(self):
        return_upc = self.find_upc()
        if not return_upc:
            assert "UPC not found for {}".format(self.current_product)
        return return_upc

    def get_price(self):
        return self.page.text_content(self.locator_product_price).strip().replace(" ", "")

    def iterate_products(self):
        # Get all products from page
        self.page.wait_for_selector(self.locator_product)
        products = self.page.query_selector_all(self.locator_product)
        print("Found products {}".format(len(products)))
        for index_product in range(len(products)):
            self.check_popup()
            self.click_product_by_index(index_product)
            # self.wait_for_element(self.locator_product_price)
            self.current_product = self.page.url
            upc = self.get_upc()
            # Check if UPC in GoogleSheet
            if upc not in self.googleSheet.upc:
                cost = self.get_price()
                # Will update GoogleSheet at the end, just in case something fails during the Scan Unlimited process
                self.update_upc_cost.append([upc, cost, self.current_product])
                print("####" * 20)
                print("Checking product: {}".format(self.current_product))
                print(cost)
                print(upc)
            # Continue
            self.page.go_back()
            # self.wait_for_element(self.locator_product)
