from pyramid.testing import setUp, tearDown, DummyRequest


def pytest_funcarg__config(request):
    def setup():
        config = setUp(settings={})
        config.include('pyramid_snippets')
        return config
    return request.cached_setup(
        setup=setup, teardown=tearDown, scope='session')


def pytest_funcarg__request(request):
    config = request.getfuncargvalue('config')
    config.manager.get()['request'] = request = DummyRequest()
    return request
