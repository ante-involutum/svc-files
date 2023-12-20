import pytest
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestFiles():

    def test_version(self):
        resp = self.bs.get(
            f'{self.url}/v1.0/version'
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_upload_object(self):
        resp = self.bs.post(
            f'{self.url}/v1.0/object',
            files={'files': open('./README.md', 'r')},
            params={
                'bucket_name': 'result'
            })
        pprint(resp.json())
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            f'{self.url}/v1.0/object',
            params={
                "prefix": "06be8094-265b-49c9-a156-7b8982004272/aomaker.html",
                'bucket_name': 'result'
            }
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_get_report(self):
        payload = {
            "uid": '06be8094-265b-49c9-a156-7b8982004272',
            "type": "aomaker",
            'path': '/data/autotest/reports'
        }
        resp = self.bs.get(
            f'{self.url}/v1.0/report',
            json=payload,
        )
        pprint(resp.json())
        assert resp.status_code == 200
