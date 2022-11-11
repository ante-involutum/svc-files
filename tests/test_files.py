import pytest


@pytest.mark.usefixtures('init')
class TestFiles():

    def test_upload(self):
        with open('./README.md', 'r') as f:
            resp = self.bs.post('/files/upload', files={'file': f})
        assert resp.status_code == 200

    def test_pull_report(self):
        resp = self.bs.get('/files/aomaker/report/199999')
        assert resp.status_code == 200
