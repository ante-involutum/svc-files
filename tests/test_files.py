import pytest


@pytest.mark.usefixtures('init')
class TestFiles():

    header = {
        "Authorization": "admin"
    }

    def test_upload(self):
        with open('./README.md', 'r') as f:
            resp = self.bs.post(
                '/files/upload', headers=self.header, files={'file': f})
        assert resp.status_code == 200

    def test_pull_report(self):
        resp = self.bs.get('/files/aomaker/report/199999', headers=self.header)
        assert resp.status_code == 200

    def test_locust_pull_report(self):
        self.bs.get('/files/locust/report/1', headers=self.header)
