import os
import pytest
from requests import Session


env = os.getenv('ENV')
host = os.getenv('HOST')


@pytest.fixture()
def init(request):
    bs = Session()
    bs.headers['Authorization'] = 'admin'
    request.cls.bs = bs
    if env == 'loc':
        request.cls.url = f'http://127.0.0.1:8004'
    else:
        request.cls.url = f'http://{host}/{env}'
