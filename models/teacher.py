from extensions import db


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100))
    subject = db.Column(db.String(100))

    def __repr__(self):
        return f"<Teacher {self.user.username}>"
