from ..utils import db
from flask import request
from ..models.students import Student,Courses, StudentCourse, Grades
from flask_jwt_extended import  get_jwt_identity, jwt_required  
from flask_restx import Namespace, Resource, fields,marshal
from http import HTTPStatus
from ..auth.views import admin_required


grades_namespace = Namespace('grades', description='Namespace for Grades')

grades_model = grades_namespace.model(
    'Grades of student', {
    'student_id' : fields.Integer(description="Student ID"),
    'course_id':fields.String(description="Course ID", required=True),
    'aggregate': fields.Float(description='score of students')
    
     
}
)



def get_grade(aggregate):
    """ Convert a score to corresponding grade """
    if aggregate <= 100 and aggregate > 89:
        return 'A'
    elif aggregate < 90 and aggregate > 79:
        return 'B'
    elif aggregate < 80 and aggregate > 69:
        return 'C'
    elif aggregate < 70 and aggregate > 59:
        return 'D'
    elif aggregate < 60 and aggregate > 49:
        return 'E'
    elif aggregate < 50 :
        return 'F'    
    else:
        return 'F'


def convert_grade_to_gpa(grade):
    """Convert a grade to the corresponding point value """
    if grade == 'A':
        return 4.0
    elif grade == 'B':
        return 3.3
    elif grade == 'C':
        return 2.3
    elif grade == 'D':
        return 1.3
    else:
        return 0.0
    



@grades_namespace.route('/course/add_score')
class AddScore(Resource):

    @grades_namespace.expect(grades_model)
    @grades_namespace.doc(
        description='''
            This endpoint is accessible only to an admin. 
            It allow admin add a student score in a course. 
            
            '''
    )
    @admin_required()
    def put(self):
        """
        Add a student course score
        """     
       
        student_id = request.json['student_id']
        course_id = request.json['course_id']
        aggregate_value = request.json['aggregate']
          
        # check if student and course exist
        student = Student.query.filter_by(id = student_id).first()
        course = Courses.query.filter_by(id=course_id).first()
        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND
       
        # check if student is registered for the course
        student_in_course = StudentCourse.query.filter_by(course_id=course.id, student_id=student.id).first() 
        if student_in_course:
            # check if the student already have a score in the course
            aggregate = Grades.query.filter_by(student_id=student_id, course_id=course_id).first()
            grade = get_grade(aggregate_value)
            if aggregate:
                aggregate.aggregate = aggregate_value
                aggregate.grade = grade
            else:
                # create a new score object and save to database
                aggregate = Grades(student_id=student_id, course_id=course_id, aggregate=aggregate_value , grade=grade)
            try:
                aggregate.save()
                return {'message': 'Score added successfully'}, HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while saving student course score'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'The student is not registered for this course'}, HTTPStatus.BAD_REQUEST
    

@grades_namespace.route('/<int:student_id>/gpa')
class StudentGPAView(Resource):

    @admin_required()
    def get(self, student_id):
        """
        Calculate a student gpa score
        """     
        student = Student.get_by_id(student_id)
            
        courses = StudentCourse.get_student_courses_by(student_id)
        total_gpa = 0
            
        for course in courses:
                grade = Grades.query.filter_by(
                        student_id=student_id, course_id=course.id
                    ).first()
                
                if grade:
                    grade = grade.grade
                    gpa = convert_grade_to_gpa(grade)
                    total_gpa += gpa
                
                cgpa = total_gpa / len(courses)
                round_cgpa = float("{:.1f}".format(cgpa))

                return {"message": f"{student.fullname}'s CGPA is {round_cgpa}"}, HTTPStatus.OK
        
@grades_namespace.route('/<int:student_id>/grades')
class GetStudentGrades(Resource):
    @grades_namespace.doc(
        description = "Retrieve a Student's Grades - Admins or Specific Student Only",
        params = {
            'student_id': "The Student's ID"
        }
    )
    @admin_required()
    def get(self, student_id):
        """
            Retrieve a Student's Grades - Admins or Specific Student Only
        """

            # Confirm existence of student
        student = Student.query.filter_by(id=student_id).first()
        if not student:
                return {"message": "Student Not Found"}, HTTPStatus.NOT_FOUND
            
            # Retrieve the student's grades        
        courses = StudentCourse.get_student_courses_by(student_id)
        resp = []

        for course in courses:
                grade_resp = {}
                grade_in_course = Grades.query.filter_by(
                        student_id=student_id, course_id=course.id
                    ).first()
                grade_resp['course_name'] = course.course_name

                if grade_in_course:
                    grade_resp['grade_id'] = grade_in_course.id
                    grade_resp['aggregate'] = grade_in_course.aggregate
                    grade_resp['grade'] = grade_in_course.grade
                else:
                    grade_resp['aggregate'] = None
                    grade_resp['grade'] = None
                
                resp.append(grade_resp)
            
                return resp, HTTPStatus.OK
        
       
    