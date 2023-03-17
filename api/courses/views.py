
from ..utils import db
from flask import request
from ..models.students import Student, Admin, Teacher, User ,Courses, StudentCourse
from flask_jwt_extended import  get_jwt_identity, jwt_required  
from flask_restx import Namespace, Resource, fields,marshal
from http import HTTPStatus


courses_namespace = Namespace('courses', description='Namespace for Courses')

courses_model = courses_namespace.model(
    'Registration of courses', {
    'id' : fields.Integer(description="course_id"),
    'course_name':fields.String(description="A name of course", required=True, 
                 enum = ['MATHS','SOCIAL_SCIENCES','ENGLISH','ENGINEERING','ACCOUNTING']),
    'course_code': fields.String(description="A course code"),
    'creditload' : fields.String(description="Creditload"),
    'teacher_id': fields.Integer(description='id of teacher')
    
     
}
)

studentcourse_model = courses_namespace.model(
    'Registered courses', {
    'name' : fields.String(description='coursename'),
    'date_registered': fields.DateTime(description='date registered')
    }
)

@courses_namespace.route('/register')
class RegisterCourse(Resource):
    
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

        authenticated_user_id = get_jwt_identity() 
        student = Student.query.filter_by(id=authenticated_user_id).first()   
        data = request.get_json()
        course = Courses.query.filter_by(id=data.get('course_id')).first()          
            #check if student has registered for the course before
        get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
        if get_student_in_course:
                return {
                    'message':'Course has already been registered'
                    } , HTTPStatus.OK
            # Register the student to the course
        add_student_to_course = StudentCourse(student_id=student.id, course_id=course.id)
        try:
                add_student_to_course.save()
                return {'message': 'Course registered successfully'} , HTTPStatus.CREATED
        except:
                db.session.rollback()
                return {'message': 'An error occurred while registering course'}, HTTPStatus.INTERNAL_SERVER_ERROR
       
        
   
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
        
        