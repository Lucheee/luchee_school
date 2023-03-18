import unittest
from api import create_app
from api.config.config import  config_dict
from api.utils import db
from api.models.user import Admin, Student
from flask_jwt_extended import create_access_token

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

        token = create_access_token(identity=admin.id)

        headers = {
            "Authorization": f"Bearer {token}"
        }


        # Register a student
        student_signup_data = {
            "fullname": "Test",
            "email": "teststudent@gmail.com",
            "password": "password"
           
        }

        response = self.client.post('/auth/register/student', json=student_signup_data, headers=headers)

        student = Student.query.filter_by(email='teststudent@gmail.com').first()

        assert student.fullname == "Test"

        assert response.status_code == 201


