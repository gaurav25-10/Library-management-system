from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from forms import validate_issue_form
from models import Book, BookIssue, Student, db


issues_bp = Blueprint("issues", __name__)


@issues_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "issued")
    query = BookIssue.query

    if status == "returned":
        query = query.filter(BookIssue.return_date.isnot(None))
    elif status == "overdue":
        query = query.filter(BookIssue.return_date.is_(None), BookIssue.due_date < date.today())
    else:
        query = query.filter(BookIssue.return_date.is_(None))

    issues = query.order_by(BookIssue.issue_date.desc()).paginate(
        page=page,
        per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=False,
    )
    return render_template("issues/list.html", issues=issues, status=status)


@issues_bp.route("/issue", methods=["GET", "POST"])
@login_required
def issue_book():
    students = Student.query.order_by(Student.name).all()
    books = Book.query.filter(Book.available_quantity > 0).order_by(Book.title).all()

    if request.method == "POST":
        errors = validate_issue_form(request.form)
        book = Book.query.get(request.form.get("book_id")) if request.form.get("book_id") else None
        student = Student.query.get(request.form.get("student_id")) if request.form.get("student_id") else None

        if not book or book.available_quantity <= 0:
            errors.append("Selected book is not available.")
        if not student:
            errors.append("Selected student was not found.")

        if not errors:
            issue = BookIssue(
                student_id=student.id,
                book_id=book.id,
                issue_date=date.fromisoformat(request.form["issue_date"]),
                due_date=date.fromisoformat(request.form["due_date"]),
            )
            book.available_quantity -= 1
            db.session.add(issue)
            db.session.commit()
            flash("Book issued successfully.", "success")
            return redirect(url_for("issues.index"))

        for error in errors:
            flash(error, "danger")

    return render_template("issues/issue_form.html", students=students, books=books, today=date.today())


@issues_bp.route("/return/<int:issue_id>", methods=["POST"])
@login_required
def return_book(issue_id):
    issue = BookIssue.query.get_or_404(issue_id)
    if issue.return_date:
        flash("This book has already been returned.", "info")
        return redirect(url_for("issues.index"))

    issue.return_date = date.today()
    issue.fine = issue.calculate_fine(issue.return_date)
    issue.book.available_quantity += 1
    db.session.commit()
    flash(f"Book returned successfully. Fine: Rs. {issue.fine:.2f}", "success")
    return redirect(url_for("issues.index", status="returned"))


@issues_bp.route("/overdue")
@login_required
def overdue():
    overdue_issues = BookIssue.query.filter(
        BookIssue.return_date.is_(None),
        BookIssue.due_date < date.today(),
    ).order_by(BookIssue.due_date).all()
    return render_template("issues/overdue.html", overdue_issues=overdue_issues)
