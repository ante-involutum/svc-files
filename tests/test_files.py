from requests import Session


class TestFiles:

    bs = Session()
    bs.headers["Authorization"] = "admin"
    bs.headers["x_atop_version"] = "1.0.10"

    # url = f"http://127.0.0.1:8004"
    url = f"http://172.16.60.10:31690/apis/files"

    def test_upload(self):

        resp = self.bs.post(
            f"{self.url}/upload/result", files={"files": open("./README.md", "r")}
        )
        assert resp.status_code == 200

    def test_get_aomaker_report(self):

        data = {
            "uid": "4bf580d6-53e1-4cf0-b0ef-1ec9b675e3f31",
            "type": "aomaker",
            "path": "/data/autotest/reports/html/index.html",
        }

        resp = self.bs.get(
            f"{self.url}/report",
            params=data,
        )
        assert resp.status_code == 200

    def test_get_hatbox_report(self):

        data = {
            "uid": "4bf580d6-53e1-4cf0-b0ef-1ec9b675e3f31",
            "type": "hatbox",
            "path": "/hatbox/Log/report/pytest_html/index.html",
        }

        resp = self.bs.get(
            f"{self.url}/report",
            params=data,
        )
        assert resp.status_code == 200

    def test_download_file(self):

        data = {
            "object": "README.md",
            "bucket": "result",
        }

        resp = self.bs.get(
            f"{self.url}/download",
            params=data,
        )
        assert resp.status_code == 200

    def test_query_objects(self):

        data = {
            "prefix": "aomaker-4bf580d6-53e1-4cf0-b0ef-1ec9b675e3f31",
            "bucket": "result",
            # "recursive": False,
        }

        resp = self.bs.get(
            f"{self.url}/query",
            params=data,
        )
        assert resp.status_code == 200

    def test_get(self):

        data = {
            "uid": "4bf580d6-53e1-4cf0-b0ef-1ec9b675e3f31",
            "type": "aomaker",
            # "path": "/data/autotest/reports/html/index.html",
            "path":'/data/autotest/reports/html/widgets/summary.json'
        }

        resp = self.bs.get(
            f"{self.url}/get",
            params=data,
        )

        assert resp.status_code == 200
