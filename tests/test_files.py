import pytest


@pytest.mark.usefixtures('init')
class TestFiles():

    def test_upload(self):
        with open('./README.md', 'r') as f:
            resp = self.bs.post('/files/upload', files={'file': f})
        assert resp.status_code == 200
