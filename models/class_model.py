# models/class_model.py
from . import db  # <-- correct, no circular import
from .student import Student
from .teacher import Teacher

class_student = db.Table(
    'class_student',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'))
)


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    def get_students(class_id):
        # Import Student inside the function to avoid circular import
        from .student import Student
        return Student.query.filter_by(class_id=class_id).all()
