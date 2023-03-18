from flask import Flask
from .config.config import config_dict
from .utils import db
from .models.user import Student, User, Admin
from .models.courses import StudentCourse, Courses
from .models.grades import Grades
from .auth.views import auth_namespace
from .students.views import students_namespace
from .courses.views import courses_namespace
from .grades.views import grades_namespace
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.exceptions import MethodNotAllowed, NotFound 



def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    load_dotenv()

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; ** token to authorize"
        }
    }

    api = Api(
        app,
        title='Student Management System',
        description='A simple student managements system',
        authorizations=authorizations,
        security='Bearer Auth'
        )
    
    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(students_namespace)
    api.add_namespace(courses_namespace)
    api.add_namespace(grades_namespace)
    
    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 404
    
    
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Admin': Admin,
            'Student' : Student,
            'Courses' : Courses,
            "StudentCourse" : StudentCourse,
            'Grades': Grades
            
        }

    return app