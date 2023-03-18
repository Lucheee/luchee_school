from ..utils import db
from ..models.user import Student
from ..models.courses import Courses, StudentCourse 
from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from ..auth.views import admin_required


courses_namespace = Namespace('courses', description='Namespace for Courses')



#serializer for registering a course
courses_model = courses_namespace.model(
    'Registration of courses', {
    'id' : fields.Integer(description="course_id"),
    'course_name':fields.String(description="A name of course", required=True),
    'course_code': fields.String(description="A course code"),
    'creditload' : fields.String(description="Creditload"),
    'teacher': fields.String(description='name of teacher')
    
     
}
)



#route to create a new course by only an admin
@courses_namespace.route('/create_course')
class CreateCourse(Resource):

    @courses_namespace.expect(courses_model)
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

        # to check if a course already exists
        course = Courses.query.filter_by(course_name=data['course_name']).first()
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


#route to update a course 
@courses_namespace.route('/<int:course_id>')
class UpdateCourse(Resource):

    @courses_namespace.expect(courses_model)
    @courses_namespace.marshal_with(courses_model)
    @courses_namespace.doc(
        description = "Update a Course's Details by ID - Admins Only",
        params = {
            'course_id': "The Course's ID"
        }
    )

    @admin_required()
    def put(self, course_id):
        """
            Update a Course's Details by ID - Admins Only
        """
        course = Courses.get_by_id(course_id)

        data = courses_namespace.payload

        course.course_name = data['course_name']
        course.course_code = data['course_code']
        course.creditload = data['creditload']
        course.teacher = data['teacher']

        db.session.commit()

        return course, HTTPStatus.OK
    
#delete a course
    @courses_namespace.doc(
        description = "Delete a Course by ID - Admins Only",
        params = {
            'course_id': "The Course's ID"
        }
    )
    @admin_required()
    def delete(self, course_id):
        """
            Delete a Course by ID - Admins Only
        """
        course = Courses.get_by_id(course_id)

        course.delete()

        return {"message": "Course Successfully Deleted"}, HTTPStatus.OK



    
#route to get all courses created     
@courses_namespace.route('/all-courses') 
class CoursesList(Resource):

    @courses_namespace.marshal_with(courses_model)
    @courses_namespace.doc(
        description="endpont for getting all courses created by the admin"
    )
    @admin_required()
    def get(self):
        """
        Get all courses

        """

        course = Courses.query.all()
        return course, HTTPStatus.OK

 

#route to get all students registered for a particular course
@courses_namespace.route('/<int:course_id>/students')
class GetAllCourseStudents(Resource):

    @courses_namespace.doc(
        description = "Get all Students Registered for a Course - Admins Only",
        params = {
            'course_id': "The Course's ID"
        }
    )
    @admin_required()
    def get(self, course_id):
        """
            Get all Students Enrolled for a Course - Admins Only
        """
        students = StudentCourse.get_reg_students_by(course_id) 
        resp = []
                
        #an alternative to using marshal with if your output in insomia keeps returning null


        for student in students:
            student_resp = {}
            student_resp['id'] = student.id
            student_resp['fullname'] = student.fullname
            student_resp['matric_no'] = student.matric_no

            resp.append(student_resp)

        return resp, HTTPStatus.OK     
        

#route for get all courses registered by a particular student
@courses_namespace.route('/<int:student_id>/courses')
class GetStudentCourses(Resource):

    @courses_namespace.marshal_with(courses_model)
    @courses_namespace.doc(
        description = "Retrieve a Student's Courses - Admins or Specific Student Only",
        params = {
            'student_id': "The Student's ID"
        }
    )
    @admin_required()
    def get(self, student_id):
        """
            Retrieve a Student's Courses - Admins or Specific Student Only
        """
            
        courses = StudentCourse.get_student_courses_by(student_id) #note that get_student_courses_by function is already created in the StudentCourse tables.
        

        return courses, HTTPStatus.OK

    
    
#route to delete a student from a course    
@courses_namespace.route('/delete-reg-student/<int:course_id>/<int:student_id>') 
class DeleteRegStudent(Resource):   
     @courses_namespace.doc(
        description='Remove a Student from a Course',
        params = {
            'course_id': "The Course's ID",
            'student_id': "The Student's ID"
        }
    )
     @admin_required()
     def delete(self, course_id, student_id):
        """
            Remove a Student from a Course - Admins Only
        """

        # Confirm existence of student and course
        course = Courses.query.filter_by(id=course_id).first()
        student = Student.query.filter_by(id=student_id).first()
        if not student or not course:
            return {"message": "Student or Course Not Found"}, HTTPStatus.NOT_FOUND
        
        # Check if student is not registered for the course
        student_in_course = StudentCourse.query.filter_by(
                student_id=student.id, course_id=course.id
            ).first()
        if not student_in_course:
            return {
                "message": 'Student not registered'
            }, HTTPStatus.NOT_FOUND

        # Remove the student from the course
        student_in_course.delete()

        return {"message": "Sucessfully deleted"}, HTTPStatus.OK