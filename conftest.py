from datetime import datetime
import pytest
import os
import allure


@pytest.hookimpl
def pytest_runtest_setup(item):
    logging_plugin = item.config.pluginmanager.get_plugin("logging-plugin")
    timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    logging_plugin.set_log_path(os.path.join('../../../argyle/argyle-qa/results', f'{item.name}_{timestamp}.log'))

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        mode = 'a' if os.path.exists('../../../argyle/argyle-qa/failures') else 'w'
        try:
            with open('../../../argyle/argyle-qa/failures', mode) as f:
                if 'page' in item.fixturenames:
                    page = item.funcargs['page']
                else:
                    print('Fail to take screen-shot')
                    return
            allure.attach(
                page.screenshot(),
                name='screenshot',
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            print('Fail to take screen-shot: {}'.format(e))

# used for scanner tests -> pytest -m scanner --integration=justworks -s -p no:cacheprovider --headful
@pytest.fixture(scope='session')
def integration(request):
    return request.config.getoption("--integration")

def pytest_addoption(parser):
    parser.addoption("--integration", action="store", default="justworks")