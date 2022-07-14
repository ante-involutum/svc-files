import pytest


@pytest.mark.usefixtures('init')
class TestController():

    def test_upload(self):
        with open('./README.md', 'r') as f:
            resp = self.bs.post('/files', files={'file': f})
        assert resp.status_code == 200

    def test_upload_v2(self):
        with open('./README.md', 'r') as f:
            resp = self.bs.post('/files/v2', files={'file': f})
        assert resp.status_code == 200

    def test_file_list(self):
        resp = self.bs.get('/files')
        assert resp.status_code == 200

    def test_remove(self):
        resp = self.bs.delete('/files/README.md')
        assert resp.status_code == 200

    def test_remake(self):
        resp = self.bs.post('/files/remake', json={'name': 'example.jmx'})
        assert resp.status_code == 200

    def test_files_plan(self):
        resp = self.bs.post('/files/v2/plan', json={
            'plan_name': 'str',
            'attachment': ['1']
        })
        assert resp.status_code == 200

    def test_files_get_plan(self):
        resp = self.bs.post('/files/v2/download/333')
        assert resp.status_code == 200
