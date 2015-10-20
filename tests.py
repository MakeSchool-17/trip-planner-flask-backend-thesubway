import server
import unittest
import json
from pymongo import MongoClient
from base64 import b64encode


# [Ben-G] Nice job extracting this into a separate function!
def create_auth_header(correct, username):
    if correct == True:
        password = "test"
    else:
        password = "testwrong"
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

    # [Ben-G] Once you've implemented the Trip API you can remove the tests for these example endpoints
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
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.post('/trip/',
        data=json.dumps(dict(
          name="Another object"
        )),
        headers=create_auth_header(True, "NewUser"),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trip/' + postedObjectID, headers=create_auth_header(True, "NewUser"))
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        # [Ben-G] You should add assertions to your test case! Without assertions
        # this code doesn't test anything and will never fail

    def test_getting_non_existent_trip(self):
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')

        response = self.app.get('/trip/55f0cbb4236f44b7f0e3cb23', headers=create_auth_header(True, "NewUser"))
        self.assertEqual(response.status_code, 404)

    def test_posting_trip(self):
        # [Ben-G] I'm assuming this is still in the works, but later this request
        # should require an authorization header
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())

        response = self.app.post('/trip/',
        data=json.dumps(dict(
            name="A trip"
        )),
        headers=create_auth_header(True, "NewUser"),
        content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A trip' in responseJSON["name"]

    def test_deleting_trip(self):
        # [Ben-G] I'm assuming this is still in the works, but later this request
        # should require an authorization header
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.post('/trip/',
        data=json.dumps(dict(
          name="ToBeDeletedTrip"
        )),
        headers=create_auth_header(True, "NewUser"),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]
        response = self.app.delete('/trip/' + postedObjectID, headers=create_auth_header(True, "NewUser"))
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/trip/' + postedObjectID, headers=create_auth_header(True, "NewUser"))
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        # [Ben-G] A good way for testing successful deletion would be to issue a GET
        # request to see if you can retrieve the deleted trip and expect the server
        # to return a 404 (Not Found) status code

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

    # [Ben-G] Would be better to name this 'test_valid_credentials' since the API doesn't
    # actually support the concept of login/logout
    def test_valid_credentials(self):
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/user/' + postedObjectID,
                                headers=create_auth_header(True, "NewUser"))
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)

    def test_verify_credentials_wrong(self):
        response = self.app.post('/user/',
        data=json.dumps(dict(
          name="NewUser",
          password="test",
        )),
        content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]
        response = self.app.get('/user/' + postedObjectID,
                                headers=create_auth_header(False, "NewUser"))
        self.assertEqual(response.status_code, 401)

    # def test_create_trip(self):
    #     pass

if __name__ == '__main__':
    unittest.main()
