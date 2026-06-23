from datetime import date

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    isbn = db.Column(db.String(40), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    publication_year = db.Column(db.Integer, nullable=False)
    issues = db.relationship("BookIssue", back_populates="book", cascade="all, delete-orphan")

    @property
    def active_issue_count(self):
        return BookIssue.query.filter_by(book_id=self.id, return_date=None).count()


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(40), unique=True, nullable=False)
    course = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    issues = db.relationship("BookIssue", back_populates="student", cascade="all, delete-orphan")


class BookIssue(db.Model):
    __tablename__ = "book_issues"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    fine = db.Column(db.Float, nullable=False, default=0)

    student = db.relationship("Student", back_populates="issues")
    book = db.relationship("Book", back_populates="issues")

    @property
    def is_returned(self):
        return self.return_date is not None

    @property
    def status(self):
        if self.is_returned:
            return "Returned"
        if self.due_date < date.today():
            return "Overdue"
        return "Issued"

    def calculate_fine(self, as_of=None):
        check_date = as_of or self.return_date or date.today()
        overdue_days = (check_date - self.due_date).days
        return max(overdue_days, 0) * 5
