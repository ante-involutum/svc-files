import pytest


@pytest.mark.usefixtures('init')
class TestController():

    def test_upload(self):
        with open('./README.md', 'r') as f:
            resp = self.bs.post('/files', files={'file': f})
        assert resp.status_code == 200

    def test_file_list(self):
        resp = self.bs.get('/files')
        assert resp.status_code == 200

    def test_remove(self):
        resp = self.bs.delete('/files/README.md')
        assert resp.status_code == 200
