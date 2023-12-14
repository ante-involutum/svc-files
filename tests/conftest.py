import os
import pytest
from requests import Session


HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
RELEASE = os.getenv('RELEASE')


@pytest.fixture()
def init(request):
    bs = Session()
    bs.headers['Authorization'] = 'admin'
    request.cls.bs = bs
    request.cls.url = f'http://{HOST}:{PORT}/{RELEASE}'
    # request.cls.url = f'http://{HOST}:{PORT}'
