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

    def test_get_report(self):
        resp = self.bs.get(
            '/files/report/result/aomaker/lunz-091143e5-464e-4704-8438-04ecc98f4b1a', headers=self.header)
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            '/files/',
            params={
                "prefix": "lunz-091143e5-464e-4704-8438-04ecc98f4b1a/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            },
            headers=self.header)
        assert resp.status_code == 200

    def test_post_object(self):
        resp = self.bs.post(
            '/files/v1.1',
            headers=self.header,
            files={'files': open('./README.md', 'r')},
            params={
                'bucket_name': 'test'
            })
        assert resp.status_code == 200

    def test_get_object_v1(self):
        resp = self.bs.get(
            '/files/v1.1',
            params={
                "prefix": "lunz-091143e5-464e-4704-8438-04ecc98f4b1a/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            },
            headers=self.header)
        assert resp.status_code == 200

    def test_get_report_v1(self):
        payload = {
            "uid": '091143e5-464e-4704-8438-04ecc98f4b1a',
            "type": "hatbox",
            'path': '/hatbox/Log/report/pytest_html'
        }
        resp = self.bs.get(
            '/files/v1.1/report',
            json=payload,
            headers=self.header)
        assert resp.status_code == 200
