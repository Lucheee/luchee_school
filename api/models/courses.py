from ..utils import db
from datetime import datetime
from .user import Student


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