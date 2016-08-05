import unittest
from bootstrap import app, db
from um import models

class UmTestCase(unittest.TestCase):

    def setUp(self):
        app.config.from_object('config.testing')
        db.create_all()
        self.app = app.test_client()

    def tearDown(self):
        db.drop_all()

    # test users
    def test_list_users(self):
        rv = self.app.get('/contacts/')
        self.assertEqual(rv.status_code, 200)
        assert '[]' in rv.data

    def test_add_user(self):
        rv = self.app.post('/contacts/', data='{"name":"User 1", "email":"user1@example.com"}')
        self.assertEqual(rv.status_code, 201)
        user = models.User.query.filter_by(name='User 1').first()
        self.assertIsNotNone(user)
        user = models.User.query.filter_by(email='user1@example.com').first()
        self.assertIsNotNone(user)

    def test_add_user_wrong_input(self):
        rv = self.app.post('/contacts/', data='{}')
        self.assertEqual(rv.status_code, 400)

    def test_show_user(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.get('/contacts/1')
        self.assertEqual(rv.status_code, 200)

    def test_edit_user(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.put('/contacts/1', data='{"name":"modUser 1", "email":"moduser1@example.com", "secret_key":"key"}')
        self.assertEqual(rv.status_code, 200)
        user = models.User.query.filter_by(name='modUser 1').first()
        self.assertIsNotNone(user)
        user = models.User.query.filter_by(email='moduser1@example.com').first()
        self.assertIsNotNone(user)

    def test_edit_user_wrong_input(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.put('/contacts/1', data='{}')
        self.assertEqual(rv.status_code, 400)

    def test_delete_user(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.delete('/contacts/1')
        self.assertEqual(rv.status_code, 200)
        user = models.User.query.filter_by(name='User 1').first()
        self.assertIsNone(user)

    # test properties
    def test_list_props(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.get('/contacts/1/properties')
        self.assertEqual(rv.status_code, 200)
        assert '[]' in rv.data

    def test_add_prop(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.post('/contacts/1/properties', data='{"key":"prop 1", "value":"val 1"}')
        self.assertEqual(rv.status_code, 201)
        user = models.User.query.filter_by(name='User 1').first()
        prop = user.properties[0]
        self.assertIsNotNone(prop)

    def test_add_prop_wrong_input(self):
        user = models.User('User 1', 'user1@example.com')
        db.session.add(user)
        db.session.commit()
        rv = self.app.post('/contacts/1/properties', data='{}')
        self.assertEqual(rv.status_code, 400)
        user = models.User.query.filter_by(name='User 1').first()
        self.assertEqual([], user.properties)

    def test_show_prop(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.add(models.Property('prop 1', 'val 1', 1))
        db.session.commit()
        rv = self.app.get('/contacts/1/properties/1')
        self.assertEqual(rv.status_code, 200)

    def test_edit_prop(self):
        user = models.User('User 1', 'user1@example.com')
        db.session.add(user)
        db.session.add(models.Property('prop 1', 'val 1', 1))
        db.session.commit()
        rv = self.app.put('/contacts/1/properties/1', data='{"key":"prop 2", "value":"val 2"}')
        self.assertEqual(rv.status_code, 200)
        user = models.User.query.filter_by(name='User 1').first()
        prop = user.properties[0]
        self.assertEqual('prop 2', prop.key)
        self.assertEqual('val 2', prop.value)

    def test_edit_prop_wrong_input(self):
        user = models.User('User 1', 'user1@example.com')
        db.session.add(user)
        db.session.add(models.Property('prop 1', 'val 1', 1))
        db.session.commit()
        rv = self.app.put('/contacts/1/properties/1', data='{}')
        self.assertEqual(rv.status_code, 400)
        user = models.User.query.filter_by(name='User 1').first()
        prop = user.properties[0]
        self.assertEqual('prop 1', prop.key)
        self.assertEqual('val 1', prop.value)

    def test_delete_prop(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.add(models.Property('prop 1', 'val 1', 1))
        db.session.commit()
        rv = self.app.delete('/contacts/1/properties/1')
        self.assertEqual(rv.status_code, 200)
        user = models.User.query.filter_by(name='User 1').first()
        self.assertEqual([], user.properties)

    # test attributes
    def test_list_attrs(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.get('/contacts/1/attributes')
        self.assertEqual(rv.status_code, 200)
        assert '[]' in rv.data

    def test_add_attr(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.post('/contacts/1/attributes', data='{"name":"attr 1"}')
        self.assertEqual(rv.status_code, 201)
        user = models.User.query.filter_by(name='User 1').first()
        attr = user.attributes[0]
        self.assertIsNotNone(attr)

    def test_add_attr_wrong_input(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.commit()
        rv = self.app.post('/contacts/1/attributes', data='{}')
        self.assertEqual(rv.status_code, 400)
        user = models.User.query.filter_by(name='User 1').first()
        self.assertEqual([], user.attributes)

    def test_show_attr(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.add(models.Attribute('attr 1',  1))
        db.session.commit()
        rv = self.app.get('/contacts/1/attributes/1')
        self.assertEqual(rv.status_code, 200)

    def test_edit_attr(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.add(models.Attribute('attr 1', 1))
        db.session.commit()
        rv = self.app.put('/contacts/1/attributes/1', data='{"name":"attr 2"}')
        self.assertEqual(rv.status_code, 200)
        user = models.User.query.filter_by(name='User 1').first()
        attr = user.attributes[0]
        self.assertEqual('attr 2', attr.name)

    def test_edit_attr_wrong_input(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.add(models.Attribute('attr 1', 1))
        db.session.commit()
        rv = self.app.put('/contacts/1/attributes/1', data='{}')
        self.assertEqual(rv.status_code, 400)
        user = models.User.query.filter_by(name='User 1').first()
        attr = user.attributes[0]
        self.assertEqual('attr 1', attr.name)

    def test_delete_attr(self):
        db.session.add(models.User('User 1', 'user1@example.com'))
        db.session.add(models.Attribute('attr 1', 1))
        db.session.commit()
        rv = self.app.delete('/contacts/1/attributes/1')
        self.assertEqual(rv.status_code, 200)
        user = models.User.query.filter_by(name='User 1').first()
        self.assertEqual([], user.attributes)

if __name__ == '__main__':
    unittest.main()