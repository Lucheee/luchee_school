from ..utils import db
from flask import request
from ..models.user import Student
from ..models.courses import Courses, StudentCourse
from flask_jwt_extended import  get_jwt_identity, jwt_required  
from flask_restx import Namespace, Resource, fields,marshal
from http import HTTPStatus
from ..auth.views import admin_required


courses_namespace = Namespace('courses', description='Namespace for Courses')





# serializer for getting student course
studentcourse_model = courses_namespace.model(
    'Get Student Course', {
    'course_id' : fields.Integer(required=True, description='course_id'),
    'student_id' : fields.Integer(requird=True, description='student ID'),
    'date_registered' : fields.DateTime(description='date registered for a course')
    }
)


#this route enables students to register for a course
@courses_namespace.route('/<int:course_id>/register/')
class RegisterStudentCourse(Resource):
    @courses_namespace.doc(
        description="This endpoint allows a student register for a course"
    )
    
    @jwt_required()
    def post(self,course_id):
        """
        Register for a course

        """  

        active_user = get_jwt_identity()
        user = Student.query.filter_by(id=active_user).first()

        if user:
            course = Courses.get_by_id(course_id)
            student = Student.get_by_id(user.id)

            if course:
            #check if student has registered for the course before
                check_if_registered = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
                if check_if_registered:
                  return {
                    'message':'Course has already been registered'
                    } , HTTPStatus.OK
                 # Register the student to the course
                reg_student_to_course = StudentCourse(
                student_id=student.id, 
                course_id=course.id
                
                )
      
                reg_student_to_course.save()
                
                #an alternative to using marshal with if your output in insomia keeps returning null
                course_student_resp = {}
                course_student_resp['course_id'] = reg_student_to_course.course_id
                course_student_resp['course_name'] = course.course_name
                course_student_resp['course_teacher'] = course.teacher
                course_student_resp['student_id'] = reg_student_to_course.student_id
                course_student_resp['student_full_name'] = student.fullname
                course_student_resp['student_matric_no'] = student.matric_no
                return course_student_resp, HTTPStatus.CREATED
        
            return {'message': 'Course does not exist'} , HTTPStatus.NOT_FOUND
        
        return {'message' : 'You are not allowed to do this'} , HTTPStatus.UNAUTHORIZED
    


