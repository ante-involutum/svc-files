import json
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

    def test_generate_report(self):
        resp = self.bs.get('/files/generate_report/ca0ac4',
                           headers=self.header)
        assert resp.status_code == 200

    def test_get_report(self):
        resp = self.bs.get('/files/report/aomaker/213ef9', headers=self.header)
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            '/files/',
            params={
                "prefix": "28b192/data/autotest/reports/html/widgets/summary.json"
            },
            headers=self.header)
        assert resp.status_code == 200
