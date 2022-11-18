import json
import pytest


@pytest.mark.usefixtures('init')
class TestFiles():

    header = {
        "Authorization": "admin"
    }

    def test_upload(self):
        resp = self.bs.post(
            '/files/upload/',
            headers=self.header,
            files={'files': open('./README.md', 'r')},
            params={
                'bucket_name': 'test'
            })
        assert resp.status_code == 200

    def test_generate_report(self):
        resp = self.bs.get(
            '/files/generate_report/result/db95fd',
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_report(self):
        resp = self.bs.get('/files/report/result/jmeter/db95fd', headers=self.header)
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            '/files/',
            params={
                "prefix": "28b192/data/autotest/reports/html/widgets/summary.json"
            },
            headers=self.header)
        assert resp.status_code == 200
