# models/class_model.py
from extensions import db
from datetime import datetime

class_student = db.Table(
    'class_student',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE')),
    db.Column('student_id', db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'))
)


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='classes')
    students = db.relationship('Student', secondary=class_student, backref='classes', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='class_obj', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_students(self):
        """Get all students in this class"""
        return self.students.all()
    
    def __repr__(self):
        return f"<Class {self.name}>"
