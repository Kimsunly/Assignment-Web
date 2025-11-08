from extensions import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    department = db.Column(db.String(100))

    # Relationship (one teacher -> many assignments)
    assignments = db.relationship("Assignment", backref="teacher", lazy=True)

    def __repr__(self):
        return f"<Teacher user_id={self.user_id}>"
