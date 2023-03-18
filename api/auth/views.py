from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import fields, Namespace, Resource
from ..models.user import Student, User, Admin
from http import HTTPStatus
from flask_jwt_extended import jwt_required,get_jwt_identity, create_access_token, create_refresh_token, get_jwt,verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import secrets
import string
from ..utils import db




auth_namespace = Namespace('auth', description='Namespace for Authentication')


#serializer for logging in a user(Admin)
login_model = auth_namespace.model (
 'Login', {
     'email' : fields.String(required=True, description="An email"),
    'password' : fields.String(required=True, description="A password")
   }

 )

#serializer for signing in a student with their matric number
signin_model = auth_namespace.model (
 'SignIn', {
    'matric_no' : fields.Integer(required=True, description="A matric number"),
    'password' : fields.String(required=True, description="A password")
   }

 )
#serializer for creating any user(Admin,Student)
user_model = auth_namespace.model(
    'User', {
        'fullname': fields.String(required=True, description="A fullname"),
        'email': fields.String(required=True, description="An email"),
        'password_hash': fields.String(required=True, description="A password")
        
    }

 ) 

#serializer for creating an admin
register_model = auth_namespace.model(
    'Register', {
        'id': fields.Integer(),
        'fullname': fields.String(required=True, description="A username"),
        'email': fields.String(required=True, description="An email"),
        'hostname': fields.String(description="an hostname"),
       # 'usertype': fields.String(description="A usertype")
      
    }
)



#function to get the usertype of a user to be used in the admin required() function below
def get_usertype(id):
    """ Get the type a user belong 
    param:
        id : user id
    """
    user = User.query.filter_by(id=id).first()
    if user:
        return user.usertype
    return None


#function to restrict access to only admin       
def admin_required():
    """
    A decorator to protect an endpoint with JSON Web Tokens.

    Any route decorated with this will require a user type of admin  to be present in the
    request before the endpoint can be called.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            print(claims)
            if get_usertype(claims['sub']) == 'admin':
                return fn(*args,**kwargs)
            return jsonify({'msg':"Admin only!"}) , HTTPStatus.UNAUTHORIZED
        return decorator
    return wrapper     




#function/command to generate random ids e.g admin hostname(HST@12345)
def random_char(length):
    """ Generate a random string 
    param:
        length : length of string to be generated"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


#route to register an admin
@auth_namespace.route('/register/admin')
class RegisterAdmin(Resource):
    @auth_namespace.expect(user_model)
    @auth_namespace.marshal_with(register_model)
    @auth_namespace.doc(
        description = "Register or create an admin"
    )
    def post(self):
        """
            Register an Admin 
        """

        data = request.get_json()

        host ='HST@' + random_char(6)

        new_user = Admin(
            fullname = data.get('fullname'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password')),
            usertype = 'admin',
            hostname = host
        )

        new_user.save()
        
        return new_user,HTTPStatus.CREATED
    
    

#function to generate student matric number e.g ALT12345
def keywords(length):
    """ Generate a random string 
    param:
        length : length of string to be generated"""
    alphabet = string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


#route for students to register
@auth_namespace.route('/register/student')
class RegisterStudent(Resource):
    @auth_namespace.expect(user_model)
    @auth_namespace.doc(
        description = "register a student"
    )
    def post(self):
        """
            Register a student 
        """

        data = request.get_json()

        matric ='ALT' + keywords(6)

        new_user = Student(
            fullname = data.get('fullname'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password')),
            usertype = 'student',
            matric_no = matric
        )

        new_user.save()

        

        response = {
            'message' : 'Registration sucessful, {}'.format(new_user.fullname),
            'Important' : 'Your matric number is {}'.format(new_user.matric_no)
        }
        
        return response, HTTPStatus.CREATED 
    


#route to log in any user(Admin or Student)
@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model)
    @auth_namespace.doc(
        description="login any user"
    )
    def post(self):
        """
            Generate JWT Token
        """
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if (user is not None) and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED



@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
            Refresh Access Token
        """
        user = get_jwt_identity()

        access_token = create_access_token(identity=user)

        return {'access_token': access_token}, HTTPStatus.OK



@auth_namespace.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        """
            Log the User Out
        """
        unset_jwt_cookies
        db.session.commit()
        return {"message": "Successfully Logged Out"}, HTTPStatus.OK