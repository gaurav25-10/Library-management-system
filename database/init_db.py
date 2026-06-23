from datetime import date, timedelta
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import Admin, Book, BookIssue, Student, db


def seed_database():
    admin = Admin(username="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    books = [
        Book(title="Python Programming", author="Reema Thareja", category="Programming", isbn="9780199480173", quantity=6, available_quantity=6, publication_year=2021),
        Book(title="Database System Concepts", author="Abraham Silberschatz", category="Database", isbn="9780078022159", quantity=4, available_quantity=4, publication_year=2019),
        Book(title="Computer Networks", author="Andrew S. Tanenbaum", category="Networking", isbn="9780132126953", quantity=5, available_quantity=5, publication_year=2020),
        Book(title="Operating System Concepts", author="Galvin", category="Operating System", isbn="9781119800361", quantity=3, available_quantity=3, publication_year=2021),
        Book(title="Web Technologies", author="Uttam K. Roy", category="Web Development", isbn="9780198066224", quantity=5, available_quantity=5, publication_year=2022),
        Book(title="Software Engineering", author="Ian Sommerville", category="Software Engineering", isbn="9780137035151", quantity=4, available_quantity=4, publication_year=2020),
    ]
    db.session.add_all(books)

    students = [
        Student(name="Aarav Sharma", roll_number="BCA2301", course="BCA", email="aarav@example.com", phone="9876543210"),
        Student(name="Priya Verma", roll_number="BCA2302", course="BCA", email="priya@example.com", phone="9876543211"),
        Student(name="Rohan Gupta", roll_number="BCA2303", course="BCA", email="rohan@example.com", phone="9876543212"),
        Student(name="Sneha Singh", roll_number="BCA2304", course="BCA", email="sneha@example.com", phone="9876543213"),
    ]
    db.session.add_all(students)
    db.session.commit()

    today = date.today()
    issues = [
        BookIssue(student_id=students[0].id, book_id=books[0].id, issue_date=today - timedelta(days=3), due_date=today + timedelta(days=4)),
        BookIssue(student_id=students[1].id, book_id=books[1].id, issue_date=today - timedelta(days=20), due_date=today - timedelta(days=8)),
        BookIssue(student_id=students[2].id, book_id=books[2].id, issue_date=today - timedelta(days=12), due_date=today - timedelta(days=5), return_date=today - timedelta(days=1), fine=20),
    ]
    for issue in issues:
        if not issue.return_date:
            book = next(book for book in books if book.id == issue.book_id)
            book.available_quantity -= 1
        db.session.add(issue)
    db.session.commit()


def init_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_database()
        print("Database initialized successfully.")
        print("Admin login: admin / admin123")


if __name__ == "__main__":
    init_database()
