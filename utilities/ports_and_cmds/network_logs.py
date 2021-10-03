import logging

import playwright
import pytest


class NetworkLogs:
    pytest.network_logs = []

    def __init__(self, page):
        self.page = page
        self.logger = logging.getLogger(__name__)

    def listen_requests(self):
        self.page.on("response", self.log_response)
        self.page.on("console", self.log_response_console)
        self.page.on("pageerror", self.log_page_error)
        self.page.on("requestfailed", self.log_requests_failed)

    def remove_listeners(self):
        self.page.remove_listener("response", self.log_response)
        self.page.remove_listener("console", self.log_response_console)
        self.page.remove_listener("pageerror", self.log_page_error)
        self.page.remove_listener("requestfailed", self.log_requests_failed)

    def log_response(self, response):
        response.finished()
        try:
            pytest.network_logs.append((str(response.url), response.body()))
            response_body = "" if "argyle-media" in str(response.url) else str(response.body())
            response_body = response_body[:3000] if len(response_body) > 3000 else response_body
            # check if message success or redirected
            if int(str(response.status)[0]) not in [2, 3]:
                print("WARNING: Error Network for url: {} , status code: {} and body {}".format(response.url,
                                                                                                response.status,
                                                                                                response_body))
        except playwright._impl._api_types.Error:
            pass

    def log_response_console(self, response):
        if response.type == "error":
            print("WARNING: Error Console")
        print(response.text)

    def log_page_error(self, response):
        print("WARNING: Exception Console")
        print(response)

    def log_requests_failed(self, response):
        print("WARNING: Requests Failed Console")
        print(response.url + ' ' + response.failure)
