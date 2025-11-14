from extensions import db
from datetime import datetime


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    file_path = db.Column(db.String(200))  # path to uploaded file

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))

    def __repr__(self):
        return f"<Assignment {self.title}>"
