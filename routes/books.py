from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from forms import validate_book_form
from models import Book, db


books_bp = Blueprint("books", __name__)


@books_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "title")
    query = Book.query

    if search:
        like = f"%{search}%"
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like)))

    sort_columns = {
        "title": Book.title,
        "author": Book.author,
        "category": Book.category,
        "available": Book.available_quantity.desc(),
    }
    query = query.order_by(sort_columns.get(sort, Book.title))
    books = query.paginate(page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False)
    return render_template("books/list.html", books=books, search=search, sort=sort)


@books_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        errors = validate_book_form(request.form)
        if Book.query.filter_by(isbn=request.form.get("isbn", "").strip()).first():
            errors.append("ISBN already exists.")

        if not errors:
            quantity = int(request.form["quantity"])
            book = Book(
                title=request.form["title"].strip(),
                author=request.form["author"].strip(),
                category=request.form["category"].strip(),
                isbn=request.form["isbn"].strip(),
                quantity=quantity,
                available_quantity=quantity,
                publication_year=int(request.form["publication_year"]),
            )
            db.session.add(book)
            db.session.commit()
            flash("Book added successfully.", "success")
            return redirect(url_for("books.index"))

        for error in errors:
            flash(error, "danger")

    return render_template("books/form.html", book=None)


@books_bp.route("/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        errors = validate_book_form(request.form)
        duplicate = Book.query.filter(Book.isbn == request.form.get("isbn", "").strip(), Book.id != book.id).first()
        if duplicate:
            errors.append("ISBN already exists.")

        if not errors:
            new_quantity = int(request.form["quantity"])
            issued_count = book.quantity - book.available_quantity
            if new_quantity < issued_count:
                flash("Quantity cannot be lower than currently issued copies.", "danger")
                return render_template("books/form.html", book=book)

            book.title = request.form["title"].strip()
            book.author = request.form["author"].strip()
            book.category = request.form["category"].strip()
            book.isbn = request.form["isbn"].strip()
            book.quantity = new_quantity
            book.available_quantity = new_quantity - issued_count
            book.publication_year = int(request.form["publication_year"])
            db.session.commit()
            flash("Book updated successfully.", "success")
            return redirect(url_for("books.index"))

        for error in errors:
            flash(error, "danger")

    return render_template("books/form.html", book=book)


@books_bp.route("/delete/<int:book_id>", methods=["POST"])
@login_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    if book.active_issue_count:
        flash("Cannot delete a book that is currently issued.", "warning")
        return redirect(url_for("books.index"))
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully.", "success")
    return redirect(url_for("books.index"))
