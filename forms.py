from datetime import date


def required(value):
    return value is not None and str(value).strip() != ""


def get_form_errors(form, required_fields):
    errors = []
    for field, label in required_fields.items():
        if not required(form.get(field)):
            errors.append(f"{label} is required.")
    return errors


def validate_book_form(form):
    errors = get_form_errors(
        form,
        {
            "title": "Title",
            "author": "Author",
            "category": "Category",
            "isbn": "ISBN",
            "quantity": "Quantity",
            "publication_year": "Publication year",
        },
    )
    try:
        quantity = int(form.get("quantity", 0))
        if quantity < 0:
            errors.append("Quantity cannot be negative.")
    except ValueError:
        errors.append("Quantity must be a valid number.")

    try:
        year = int(form.get("publication_year", 0))
        if year < 1000 or year > date.today().year:
            errors.append("Publication year must be realistic.")
    except ValueError:
        errors.append("Publication year must be a valid number.")
    return errors


def validate_student_form(form):
    errors = get_form_errors(
        form,
        {
            "name": "Name",
            "roll_number": "Roll number",
            "course": "Course",
            "email": "Email",
            "phone": "Phone number",
        },
    )
    if form.get("email") and "@" not in form.get("email"):
        errors.append("Email address is invalid.")
    if form.get("phone") and len(form.get("phone").strip()) < 10:
        errors.append("Phone number must contain at least 10 digits.")
    return errors


def validate_issue_form(form):
    errors = get_form_errors(
        form,
        {
            "student_id": "Student",
            "book_id": "Book",
            "issue_date": "Issue date",
            "due_date": "Due date",
        },
    )
    try:
        issue_date = date.fromisoformat(form.get("issue_date", ""))
        due_date = date.fromisoformat(form.get("due_date", ""))
        if due_date < issue_date:
            errors.append("Due date cannot be before issue date.")
    except ValueError:
        errors.append("Issue date and due date must be valid dates.")
    return errors
