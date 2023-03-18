from ..utils import db
from flask import request
from ..models.user import Student
from ..models.courses import Courses, StudentCourse
from ..models.grades import Grades
from flask_jwt_extended import  get_jwt_identity, jwt_required  
from flask_restx import Namespace, Resource, fields,marshal
from http import HTTPStatus
from ..auth.views import admin_required


grades_namespace = Namespace('grades', description='Namespace for Grades')


#serializer to add aggregate scores to a student course 
grades_model = grades_namespace.model(
    'Grades of student', {
    'student_id' : fields.Integer(description="Student ID"),
    'course_id':fields.String(description="Course ID", required=True),
    'aggregate': fields.Float(description='score of students')
    
     
}
)


#serializer to update student grades/aggregate
update_grades_model = grades_namespace.model(
    'Update Grades', {
    'aggregate': fields.Float(description='Score of students')
    }
)


#function to get the  equivalent letter grade by getting the aggregate score
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


#function to get a gpa of a student using the grades of the student
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
    


#route to add scores to the students course
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
    


#route to update a particular grade for student
@grades_namespace.route('/grades/<int:grade_id>')
class UpdateDeleteGrade(Resource):

    @grades_namespace.expect(update_grades_model)
    @grades_namespace.doc(
        description = "Update a Grade - Admins Only",
        params = {
            'grade_id': "The Grade's ID"
        }
    )
    @admin_required()
    def put(self, grade_id):
        """
            Update a Grade - Admins Only
        """
        data = grades_namespace.payload

        grade = Grades.get_by_id(grade_id)
        
        grade.aggregate = data['aggregate']
        grade.grade = get_grade(data['aggregate'])
        
        db.session.commit()

        grade_resp = {}
        grade_resp['grade_id'] = grade.id
        grade_resp['student_id'] = grade.student_id
        grade_resp['course_id'] = grade.course_id
        grade_resp['aggregate'] = grade.aggregate
        grade_resp['grade'] = grade.grade

        return grade_resp, HTTPStatus.OK
    

    #endpoint for deleting a particular grade
    @grades_namespace.doc(
        description = "Delete a Grade - Admins Only",
        params = {
            'grade_id': "The Grade's ID"
        }
    )
    @admin_required()
    def delete(self, grade_id):
        """
            Delete a Grade - Admins Only
        """
        grade = Grades.get_by_id(grade_id)
        
        grade.delete()

        return {"message": "Grade Successfully Deleted"}, HTTPStatus.OK
    

#route for getting the gpa of a student
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
                #to check for the grades of student
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
        

#route to get a particular student grades      
@grades_namespace.route('/<int:student_id>/grades')
class GetStudentGrades(Resource):
    @grades_namespace.doc(
        description = "Retrieve a Student's Grades - Admins",
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
        
       
    