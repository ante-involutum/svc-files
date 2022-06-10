import pytest

from requests_toolbelt.sessions import BaseUrlSession


@pytest.fixture()
def init(request):
    bs = BaseUrlSession(base_url='http://127.0.0.1:8004')
    request.cls.bs = bs
