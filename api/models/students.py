from ..utils import db
from datetime import datetime
from enum import Enum


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer(), primary_key=True)
    fullname = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    usertype = db.Column(db.String(10))

    __mapper_args__ = {
        'polymorphic_on' : usertype,
        'polymorphic_identity' : 'users'
    }

    def __repr__(self):
        return f"<User {self.fullname}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Student(User):
    __tablename__ = 'students' 

    id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    matric_no = db.Column(db.String(20))
    
    __mapper_args__ = {
        'polymorphic_identity' : 'student'
    }
    

    def save(self):
        db.session.add(self)
        db.session.commit()
        

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    

class Admin(User):
     __tablename__ = 'admin'

     id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
     hostname = db.Column(db.String(40), nullable = False, unique=True)
     

     __mapper_args__ = {
        
        'polymorphic_identity' : 'admin'
    }
     def __repr__(self):
        return f"<Hostname {self.hostname}>"

     def save(self):
        db.session.add(self)
        db.session.commit()
        
     @classmethod
     def get_by_id(cls, id):
        return cls.query.get_or_404(id)
     

     def delete(self):
        db.session.delete(self)
        db.session.commit()
     



class Courses(db.Model):
   __tablename__ = 'courses'

   id = db.Column(db.Integer(), primary_key = True)
   course_name = db.Column(db.String(20), nullable=False)
   course_code = db.Column(db.String(20), nullable=False)
   creditload = db.Column(db.String(60), nullable=False)
   teacher = db.Column(db.Integer(),nullable=False)


     
   def save(self):
        db.session.add(self)
        db.session.commit()

   def delete(self):
          db.session.delete(self)
          db.session.commit()
        
   @classmethod
   def get_by_id(cls, id):
        return cls.query.get_or_404(id) 
  

class StudentCourse(db.Model):
      __tablename__ = 'student_course'

      id = db.Column(db.Integer(),primary_key = True)
      course_id = db.Column(db.Integer(), db.ForeignKey('courses.id'), nullable=False)
      student_id = db.Column(db.Integer(),db.ForeignKey('students.id'), nullable=False)
      date_registered = db.Column(db.DateTime(), default=datetime.utcnow)

      
      def save(self):
        db.session.add(self)
        db.session.commit()

      def delete(self):
          db.session.delete(self)
          db.session.commit()
        
      @classmethod
      def get_by_id(cls, id):
        return cls.query.get_or_404(id)
      
      @classmethod
      def get_reg_students_by(cls, course_id):
        students = (
            Student.query.join(StudentCourse)
            .join(Courses).filter(Courses.id == course_id).all()
        )
        return students
    

      @classmethod
      def get_student_courses_by(cls, student_id):
        courses = (
            Courses.query.join(StudentCourse)
            .join(Student).filter(Student.id == student_id).all()
        )
        return courses
      



class Grades(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    aggregate = db.Column(db.Float , nullable=False)
    grade = db.Column(db.String(5) , nullable=True )
    created_at = db.Column(db.DateTime() , nullable=False , default=datetime.utcnow)



    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
