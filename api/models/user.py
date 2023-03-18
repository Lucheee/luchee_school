from ..utils import db
from datetime import datetime


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
    
      