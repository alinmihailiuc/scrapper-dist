import logging
from playwright.sync_api import Page
import pytest
import os
from playwright._impl._api_types import TimeoutError
import utilities.test_resources as test_resources
from retry import retry
from playwright._impl._api_types import Error as playwright_error


class Base(object):
    def __init__(self, page: Page):
        self.page = page
        # Logger
        self.logger = logging.getLogger(__name__)
        env = 'dev' if 'ENV' not in os.environ else os.environ.get('ENV').lower()
        env_name = '' if env == "prod" else 'develop.'

        self.live_link_item = "Better Borrowing Now, Inc"
        self.live_email = "patricia.johnson@betterborrowingnow.com"
        self.live_password = "Jesus4356"
        self.test_resources = os.path.abspath(os.path.join(test_resources.__file__, os.pardir))

        # Initialized in api create_client_account
        # pytest.new_email = None
        # pytest.client_id = None
        # pytest.new_sandbox_id = None
        # pytest.new_sandbox_secret = None
        # pytest.new_production_id = None
        # pytest.new_production_secret = None

    def wait_element_appear_disappear(self, element_locator, appearance_time=4000, disappearance_time=90000):
        self.page.wait_for_selector(element_locator, appearance_time)
        self.page.wait_for_selector(element_locator, disappearance_time, "detached")

    @retry(AssertionError, tries=3, delay=2)
    def check_text_from_locator(self, locator, expected_text):
        self.page.wait_for_selector(locator, 5000)
        actual_text = self.page.text_content(locator)
        print("At locator {} found text {}".format(locator, expected_text))
        assert actual_text == expected_text, 'Test expected to find {} but found {}'.format(expected_text, actual_text)

    def check_if_element_exists(self, locator):
        elements = self.get_number_of_elements(locator)
        if elements > 0:
            # print("Element {} exists".format(locator))
            return True
        else:
            return False

    @retry(playwright_error, tries=3, delay=3)
    def get_number_of_elements(self, locator):
        return len(self.page.query_selector_all(locator))

    def check_click_failed(self, selector):
        try:
            self.page.click(selector)
            return False
        except TimeoutError:
            return True

    def get_element_locator_by_index(self, locator_xpath, index):
        # xpath begins from 1
        index = int(index) + 1
        return_locator = "({})[{}]".format(locator_xpath, index)
        # print("Returning locator: {}".format(return_locator))
        return return_locator

    def get_input_content(self, locator_xpath_input):
        return self.page.get_attribute(locator_xpath_input, "value")

    def get_no_elements_having_text_equal_with(self, text):
        locator = "//*[text()='{}']".format(text)
        print("Getting number of elements for locator {}".format(locator))
        return self.get_number_of_elements(locator)

    @retry(TimeoutError, tries=5, delay=2)
    def click_on_element_until_element_disappear(self, click_element_locator, disappear_element_locator):
        self.page.click(click_element_locator)
        self.page.wait_for_selector(disappear_element_locator, 3000, "detached")

    @retry(TimeoutError, tries=5, delay=2)
    def click_on_element_until_element_appear(self, click_element_locator, appear_element_locator):
        self.page.click(click_element_locator)
        self.page.wait_for_selector(appear_element_locator, 3000)

    @retry(playwright_error, tries=3, delay=2)
    def click_on_element(self, click_element_locator):
        self.page.click(click_element_locator)

    @retry(playwright_error, tries=3, delay=2)
    def fill_on_element(self, click_element_locator, value):
        self.page.fill(click_element_locator, value)

    @retry(playwright_error, tries=3, delay=3)
    def wait_for_element(self, locator):
        try:
            self.page.wait_for_selector(locator)
        except:
            self.page.reload()
            raise playwright_error("Playwright error")
