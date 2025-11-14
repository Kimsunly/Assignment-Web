from .user import User
from .student import Student
from .teacher import Teacher
from .assignment import Assignment

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
