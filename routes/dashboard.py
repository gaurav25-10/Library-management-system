from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required

from models import Book, BookIssue, Student


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    total_books = Book.query.count()
    total_students = Student.query.count()
    issued_books = BookIssue.query.filter_by(return_date=None).count()
    returned_books = BookIssue.query.filter(BookIssue.return_date.isnot(None)).count()
    overdue_books = BookIssue.query.filter(
        BookIssue.return_date.is_(None),
        BookIssue.due_date < date.today(),
    ).count()

    category_rows = Book.query.with_entities(Book.category).all()
    category_counts = {}
    for row in category_rows:
        category_counts[row.category] = category_counts.get(row.category, 0) + 1

    recent_issues = BookIssue.query.order_by(BookIssue.issue_date.desc()).limit(6).all()

    return render_template(
        "dashboard.html",
        stats={
            "total_books": total_books,
            "total_students": total_students,
            "issued_books": issued_books,
            "returned_books": returned_books,
            "overdue_books": overdue_books,
        },
        category_counts=category_counts,
        recent_issues=recent_issues,
    )
