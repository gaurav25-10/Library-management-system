from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from forms import validate_student_form
from models import Student, db


students_bp = Blueprint("students", __name__)


@students_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "name")
    query = Student.query

    if search:
        like = f"%{search}%"
        query = query.filter(or_(Student.name.ilike(like), Student.roll_number.ilike(like), Student.course.ilike(like)))

    sort_columns = {
        "name": Student.name,
        "roll": Student.roll_number,
        "course": Student.course,
    }
    students = query.order_by(sort_columns.get(sort, Student.name)).paginate(
        page=page,
        per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=False,
    )
    return render_template("students/list.html", students=students, search=search, sort=sort)


@students_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        errors = validate_student_form(request.form)
        if Student.query.filter_by(roll_number=request.form.get("roll_number", "").strip()).first():
            errors.append("Roll number already exists.")
        if Student.query.filter_by(email=request.form.get("email", "").strip()).first():
            errors.append("Email already exists.")

        if not errors:
            student = Student(
                name=request.form["name"].strip(),
                roll_number=request.form["roll_number"].strip(),
                course=request.form["course"].strip(),
                email=request.form["email"].strip(),
                phone=request.form["phone"].strip(),
            )
            db.session.add(student)
            db.session.commit()
            flash("Student added successfully.", "success")
            return redirect(url_for("students.index"))

        for error in errors:
            flash(error, "danger")

    return render_template("students/form.html", student=None)


@students_bp.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == "POST":
        errors = validate_student_form(request.form)
        roll_duplicate = Student.query.filter(
            Student.roll_number == request.form.get("roll_number", "").strip(),
            Student.id != student.id,
        ).first()
        email_duplicate = Student.query.filter(
            Student.email == request.form.get("email", "").strip(),
            Student.id != student.id,
        ).first()
        if roll_duplicate:
            errors.append("Roll number already exists.")
        if email_duplicate:
            errors.append("Email already exists.")

        if not errors:
            student.name = request.form["name"].strip()
            student.roll_number = request.form["roll_number"].strip()
            student.course = request.form["course"].strip()
            student.email = request.form["email"].strip()
            student.phone = request.form["phone"].strip()
            db.session.commit()
            flash("Student updated successfully.", "success")
            return redirect(url_for("students.index"))

        for error in errors:
            flash(error, "danger")

    return render_template("students/form.html", student=student)


@students_bp.route("/delete/<int:student_id>", methods=["POST"])
@login_required
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    active_issues = [issue for issue in student.issues if issue.return_date is None]
    if active_issues:
        flash("Cannot delete a student with active issued books.", "warning")
        return redirect(url_for("students.index"))
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully.", "success")
    return redirect(url_for("students.index"))
