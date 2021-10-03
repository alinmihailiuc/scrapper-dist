from retry import retry

class AssertUtils(object):

    @retry(AssertionError, tries=10, delay=2)
    def check_content_refresher(self, get_actual_function, expected_content):
        actual = get_actual_function()
        assert actual == expected_content, 'Expected {} Actual {}'.format(expected_content, actual)
