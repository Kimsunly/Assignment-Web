from extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    major = db.Column(db.String(100))
    year = db.Column(db.String(10))
    section = db.Column(db.String(20))

    def __repr__(self):
        return f"<Student {self.user.username}>"
