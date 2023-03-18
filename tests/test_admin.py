import unittest
from api import create_app
from api.config.config import  config_dict
from api.utils import db
from api.models.user import Admin
from flask_jwt_extended import create_access_token
from flask import json

class UserTestCase(unittest.TestCase):
    
    def setUp(self):

        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()
        

    def tearDown(self):

        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


    def test_admin(self):

        # Register an admin
        admin_signup_data = {
            "fullname": "Test",
            "hostname": "HST123455",
            "email": "testadmin@gmail.com",
            "password": "password",
            'usertype': "admin"
        }

        response = self.client.post('/auth/register/admin', json=admin_signup_data)

        admin = Admin.query.filter_by(email='testadmin@gmail.com').first()

        assert admin.fullname == "Test"

        assert response.status_code == 201


     # Sign an admin in
        admin_login_data = {
            "email":"testadmin@gmail.com",
            "password": "password"
        }
        response = self.client.post('/auth/login', json=admin_login_data)

        assert response.status_code == 201

        
        
        
        token = create_access_token(identity=admin.id)

        headers = {
            "Authorization": f"Bearer {token}"
        }


      # Retrieve all admins
        response = self.client.get('/students/all_admins', headers=headers)

        print (json.loads(response))

        assert response.status_code == 200

        assert response.json == []       