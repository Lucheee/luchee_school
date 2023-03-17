
from ..utils import db
from flask import request
from ..models.students import Student, Admin, Teacher, User 
from flask_jwt_extended import  get_jwt_identity, jwt_required  
from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from ..auth.views import admin_required, user_model, register_model

students_namespace = Namespace('students', description='Namespace for Students')

#serializer for getting all students
student_model = students_namespace.model(
    'student', {
        'id': fields.Integer(description='Student ID'),
        'fullname': fields.String(required=True, description="A fullname"),
        'email': fields.String(required=True, description="An email"),
        'matric_no': fields.String(required=True, description="A password") 

    }

 ) 

#route to get all students by admin only
@students_namespace.route('/all_students')
class GetStudents(Resource):

    @students_namespace.marshal_with(student_model)
    @students_namespace.doc(
        description='Get all students'
    )
    @admin_required() 
    def get(self):
        """
        Retrieve all students in school
        """
        students = User.query.all()
        return students, HTTPStatus.OK
    
    
#get a particular student by id
@students_namespace.route('/<int:student_id>')
class RetrieveStudent(Resource):

    @students_namespace.marshal_with(student_model)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to an admin. 
            It is to retrieve a student by Id
            """
    )
    @admin_required()
    def get(self, student_id):
        """
        Retrieve a student 
        """
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return {'message':'Student does not exist'}, HTTPStatus.NOT_FOUND
        return student , HTTPStatus.OK
    

#Note, you can just query the User table and filter by user_id to get all users(students, admin, teachers) instead of getting them individually.

#route to get all admin by admin only
@students_namespace.route('/all_admins')
class GetAdmins(Resource):

    @students_namespace.marshal_with(register_model)
    @students_namespace.doc(
        description='Get all Admin'
    )
    @admin_required() 
    def get(self):
        """
        Retrieve all students in school
        """
        admin = Admin.query.all()
        return admin, HTTPStatus.OK

#route to update student data
@students_namespace.route('/update')
class UpdateStudent(Resource):
    @students_namespace.expect(user_model)
    @students_namespace.marshal_with(student_model)
    @students_namespace.doc(
        description='Update a student by JWT',
        
    )     

    @jwt_required()
    def put(self):
            """
            Update a Student by ID
            """
            active_student = get_jwt_identity() 
            print(active_student)
            user = User.query.filter_by(id=active_student).first()       
                 
            data = students_namespace.payload

            email_exists = User.query.filter_by(email=data["email"]).first() # method of checking if email because of the uniqueness of email in my user table

            if email_exists:
                 return {"message":"Email already exists"}, HTTPStatus.BAD_REQUEST    
             
            user.fullname = data["fullname"]
            user.email = data["email"]

            db.session.commit()
           
            return user, HTTPStatus.OK
            
            
 #route to delete student data to be accessed by admin only
@students_namespace.route('/delete/<int:user_id>')
class Delete(Resource):
    @students_namespace.doc(
        description='Delete a user by ID',
    )    
    @admin_required()
    def delete(self, user_id):
        """
            Delete a User by ID

        """
        
        user = User.get_by_id(id=user_id)

        user.delete()

        #active_student = get_jwt_identity() 
        #    print(active_student)
          #  user = User.query.filter_by(id=active_student).first() 

        return {"message": "User Deleted Successfully"}, HTTPStatus.OK
        
        

       