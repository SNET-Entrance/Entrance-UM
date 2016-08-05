import unittest
from bootstrap import app, db
from cm import models

class UmTestCase(unittest.TestCase):

    def setUp(self):
        app.config.from_object('config.testing')
        db.create_all()
        self.app = app.test_client()

    def tearDown(self):
        db.drop_all()

    def test_list_container(self):
        rv = self.app.get('/container/')
        self.assertEqual(rv.status_code, 200)
        assert '[]' in rv.data

    def test_add_container(self):
        rv = self.app.post('/container/', data='{"name":"Gallery", "path":"/home/user/pictures/gallery", "files": [{ "path":"/home/user/pictures/gallery/picture1.png", "type":"PABE14", "policy":"all" }]}')
        self.assertEqual(rv.status_code, 201)
        container = models.Container.query.filter_by(name='Gallery').first()
        self.assertIsNotNone(container)

    def test_add_container_wrong_input(self):
        rv = self.app.post('/container/', data='{}')
        self.assertEqual(rv.status_code, 400)

    def test_show_container(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()
        rv = self.app.get('/container/1')
        self.assertEqual(rv.status_code, 200)

    def test_edit_container(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()
        rv = self.app.put('/container/1', data='{"name":"Gallery 1", "path":"/home/user/pictures/gallery"}')
        self.assertEqual(rv.status_code, 200)
        container = models.Container.query.filter_by(name='Gallery 1').first()
        self.assertIsNotNone(container)

    def test_edit_container_wrong_input(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()
        rv = self.app.put('/container/1', data='{"name":"Gallery 1"}')
        self.assertEqual(rv.status_code, 400)

    def test_delete_container(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()
        rv = self.app.delete('/container/1')
        self.assertEqual(rv.status_code, 200)
        container = models.Container.query.filter_by(name='Gallery').first()
        self.assertIsNone(container)

    def test_list_files(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()

        rv = self.app.get('/container/1')
        self.assertEqual(rv.status_code, 200)
        assert '[]' in rv.data

    def test_add_file(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()

        rv = self.app.post('/container/1/files/', data='{"path":"/home/user/pictures/gallery/picture4.png", "type":"PABE14", "policy":"all"}')
        self.assertEqual(rv.status_code, 201)
        file = models.File.query.filter_by(path='/home/user/pictures/gallery/picture4.png').first()
        self.assertIsNotNone(file)

    def test_add_file_wrong_input(self):
        db.session.add(models.Container('Gallery', '/home/user/pictures/gallery'))
        db.session.commit()

        rv = self.app.post('/container/1/files/', data='{}')
        self.assertEqual(rv.status_code, 400)
        file = models.File.query.filter_by(path='/home/user/pictures/gallery/picture4.png').first()
        self.assertIsNone(file)

    def test_show_file(self):
        container = models.Container('Gallery', '/home/user/pictures/gallery')
        db.session.add(container)
        db.session.commit()
        file = models.File('/home/user/pictures/gallery/picture4.png', 'PABE14', 'all', container.id)
        db.session.add(file)
        db.session.commit()

        rv = self.app.get('/container/1/files/1')
        self.assertEqual(rv.status_code, 200)

    def test_edit_file(self):
        container = models.Container('Gallery', '/home/user/pictures/gallery')
        db.session.add(container)
        db.session.commit()
        file = models.File('/home/user/pictures/gallery/picture4.png', 'PABE14', 'all', container.id)
        db.session.add(file)
        db.session.commit()

        rv = self.app.put('/container/1/files/1', data='{"path":"/home/user/pictures/gallery/picture5.png", "type":"PABE15", "policy":"alle"}')
        self.assertEqual(rv.status_code, 200)
        file = models.File.query.filter_by(path='/home/user/pictures/gallery/picture5.png').first()
        self.assertIsNotNone(file)

    def test_edit_file_wrong_input(self):
        container = models.Container('Gallery', '/home/user/pictures/gallery')
        db.session.add(container)
        db.session.commit()
        file = models.File('/home/user/pictures/gallery/picture4.png', 'PABE14', 'all', container.id)
        db.session.add(file)
        db.session.commit()

        rv = self.app.put('/container/1/files/1', data='{}')
        self.assertEqual(rv.status_code, 400)
        file = models.File.query.filter_by(path='/home/user/pictures/gallery/picture5.png').first()
        self.assertIsNone(file)

    def test_delete_file(self):
        container = models.Container('Gallery', '/home/user/pictures/gallery')
        db.session.add(container)
        db.session.commit()
        file = models.File('/home/user/pictures/gallery/picture4.png', 'PABE14', 'all', container.id)
        db.session.add(file)
        db.session.commit()

        rv = self.app.delete('/container/1/files/1')
        self.assertEqual(rv.status_code, 200)
        file = models.File.query.filter_by(id=1).first()
        self.assertIsNone(file)

if __name__ == '__main__':
    unittest.main()