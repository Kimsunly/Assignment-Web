from extensions import db


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        "teachers.id"), nullable=False)

    # Relationship (one assignment -> many submissions)
    submissions = db.relationship(
        "Submission", backref="assignment", lazy=True)

    def __repr__(self):
        return f"<Assignment {self.title}>"

# (Optional: add Submission model here or create models/submission.py)


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(
        "assignments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey(
        "students.id"), nullable=False)
    file_path = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Submission {self.id}>"
