import pytest


@pytest.mark.usefixtures('init')
class TestFiles():

    def test_upload(self):
        resp = self.bs.post(
            f'{self.url}/files/upload/',
            files={'files': open('./README.md', 'r')},
            params={
                'bucket_name': 'test'
            })
        assert resp.status_code == 200

    def test_get_report(self):
        resp = self.bs.get(
            f'{self.url}/files/report/result/aomaker/aomaker-091143e5-464e-4704-8438-04ecc98f4b1a')
        assert resp.status_code == 200

    def test_tasks(self):
        resp = self.bs.get(f'{self.url}/files/tasks')
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            f'{self.url}/files/',
            params={
                "prefix": "hatbox-091143e5-464e-4704-8438-04ecc98f4b1a/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            }
        )
        assert resp.status_code == 200

    def test_post_object(self):
        resp = self.bs.post(
            f'{self.url}/files/v1.1',
            files={'files': open('./README.md', 'r')},
            params={
                'bucket_name': 'test'
            })
        assert resp.status_code == 200

    def test_get_object_v1(self):
        resp = self.bs.get(
            f'{self.url}/files/v1.1',
            params={
                "prefix": "hatbox-091143e5-464e-4704-8438-04ecc98f4b1a/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            }
        )
        assert resp.status_code == 200

    def test_get_report_v1(self):
        payload = {
            "uid": '091143e5-464e-4704-8438-04ecc98f4b1a',
            "type": "hatbox",
            'path': '/hatbox/Log/report/pytest_html'
        }
        resp = self.bs.get(
            f'{self.url}/files/v1.1/report',
            json=payload,
        )
        assert resp.status_code == 200
