from extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    major = db.Column(db.String(100))

    # Relationship (one student -> many submissions)
    submissions = db.relationship("Submission", backref="student", lazy=True)

    def __repr__(self):
        return f"<Student user_id={self.user_id}>"
