import server
import unittest
import json
from pymongo import MongoClient
from base64 import b64encode


def create_auth_header():
    username = "NewUser"
    password = "test"
    pw_str = "{0}:{1}".format(username, password)
    # encoded = pw_str.encode("utf-8")
    # encoded = str.encode(pw_str)

    auth = 'Basic ' + b64encode(pw_str.encode('utf-8')).decode('utf-8')
    return {"Authorization": auth}
    # resulting header: "Authorization: Basic TmV3VXNlcjp0ZXN0"


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('myobjects')
        db.drop_collection('trips')
        db.drop_collection('users')

    # MyObject tests

    def test_posting_myobject(self):
        response = self.app.post('/myobject/',
        data=json.dumps(dict(
            name="A object"
        )),
        content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A object' in responseJSON["name"]

    def test_getting_obj(self):
        response = self.app.post('/myobject/',
        data=json.dumps(dict(
          name="Another object"
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/myobject/' + postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another object' in responseJSON["name"]

    def test_getting_non_existent_obj(self):
        response = self.app.get('/myobject/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

    # Trip tests

    def test_getting_trip(self):
        response = self.app.post('/trip/',
        data=json.dumps(dict(
          name="Another object"
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trip/' + postedObjectID)
        responseJSON = json.loads(response.data.decode())

    def test_getting_non_existent_trip(self):
        response = self.app.get('/trip/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

    def test_posting_trip(self):
        response = self.app.post('/trip/',
        data=json.dumps(dict(
            name="A trip"
        )),
        content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A trip' in responseJSON["name"]

    def test_deleting_trip(self):
        response = self.app.post('/trip/',
        data=json.dumps(dict(
          name="ToBeDeletedTrip"
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]
        response = self.app.delete('/trip/' + postedObjectID)
        self.assertEqual(response.status_code, 200)

    # User tests

    def test_signup_user(self):
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')

        responseJSON = json.loads(response.data.decode())
        assert 'application/json' in response.content_type
        assert 'NewUser' in responseJSON["name"]
        assert 'password' not in responseJSON
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/user/' + postedObjectID,
                                headers=create_auth_header())
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)

    # def test_create_trip(self):
    #     pass

    # def test_verify_credentials_wrong(self):
    #     pass

if __name__ == '__main__':
    unittest.main()
