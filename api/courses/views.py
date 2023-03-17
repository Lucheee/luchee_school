
from ..utils import db
from flask import request
from ..models.students import Student, Admin, Teacher, User ,Courses, StudentCourse
from flask_jwt_extended import  get_jwt_identity, jwt_required  
from flask_restx import Namespace, Resource, fields,marshal
from http import HTTPStatus
from ..auth.views import admin_required


courses_namespace = Namespace('courses', description='Namespace for Courses')

courses_model = courses_namespace.model(
    'Registration of courses', {
    'id' : fields.Integer(description="course_id"),
    'course_name':fields.String(description="A name of course", required=True),
    'course_code': fields.String(description="A course code"),
    'creditload' : fields.String(description="Creditload"),
    'teacher': fields.String(description='name of teacher')
    
     
}
)

studentcourse_model = courses_namespace.model(
    'Registered courses', {
    'name' : fields.String(description='coursename'),
    'date_registered': fields.DateTime(description='date registered')
    }
)

@courses_namespace.route('/create_course')
class CreateCourse(Resource):

    @courses_namespace.expect(courses_model)
    @courses_namespace.marshal_with(courses_model)
    @courses_namespace.doc(
        description="""
            This endpoint allows an admin create a  course
            """
    )
    
    @admin_required()
    def post(self):
        """
        Create a new course

        """

        data = courses_namespace.payload

        # Check if course already exists
        course = Courses.query.filter_by(name=data['course_name']).first()
        if course:
            return {"message": "Course Already Exists"}, HTTPStatus.CONFLICT

        # Register new course
        new_course = Courses(
            course_name = data['course_name'],
            course_code = data['course_code'],
            creditload = data['creditload'],
            teacher = data['teacher']
        )

        new_course.save()

        

        return {'message': 'Sucessfully created'}, HTTPStatus.CREATED


@courses_namespace.route('/register')
class RegisterStudentCourse(Resource):
    
    @courses_namespace.expect(courses_model)
    @courses_namespace.doc(
        description="""
            This endpoint allows a student register for a course
            """
    )
    
    @jwt_required()
    def post(self):
        """
        Register for a course

        """
        active_user = get_jwt_identity() 
        user = Student.query.filter_by(id=active_user).first()   
        data = request.get_json()
        course = Courses.query.filter_by(id=data.get('course_id')).first()  
        if course:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(user_id=user.matric_no, course_id=course.id).first()
            if get_student_in_course:
               return {
                    'message':'Course has already been registered'
                    } , HTTPStatus.OK
            # Register the student to the course
            add_student_to_course = StudentCourse(user_id=user.matric_no, course_id=course.id)

            
        
            add_student_to_course.save()
            return add_student_to_course, HTTPStatus.CREATED
        
        return {'message': 'Course does not exist'} , HTTPStatus.NOT_FOUND
        
   
@courses_namespace.route('/<int:student_id>/courses')
class StudentCoursesList(Resource):

    @courses_namespace.marshal_with(courses_model)
    @jwt_required
    def get(self, student_id):
        """
        Retrieve a student courses
        """     
        courses = StudentCourse.get_student_courses(student_id)
        return courses , HTTPStatus.OK        
        
        