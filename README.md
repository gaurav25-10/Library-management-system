# Library Management System

A complete Flask-based Library Management System suitable for a BCA final year project. It includes secure admin login, dashboard statistics, book and student management, issue/return workflow, automatic overdue fine calculation, reports, PDF export, Excel export, pagination, search, sorting, and a responsive Bootstrap 5 interface.

https://library-management-system-pqnw.onrender.com/

## Technology Stack

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- Database: SQLite
- ORM: SQLAlchemy
- Authentication: Flask-Login
- Password Hashing: Werkzeug Security
- Reports: ReportLab and OpenPyXL

## Folder Structure

```text
library_management_system/
├── app.py
├── run.py
├── requirements.txt
├── models.py
├── forms.py
├── config.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── books.py
│   ├── dashboard.py
│   ├── students.py
│   ├── issues.py
│   └── reports.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── _pagination.html
│   ├── auth/
│   ├── books/
│   ├── students/
│   ├── issues/
│   ├── reports/
│   └── errors/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
└── database/
    ├── init_db.py
    └── library.db
```

## Main Features

- Admin login and logout with session management
- Dashboard cards for total books, students, issued books, returned books, and overdue books
- Chart.js dashboard charts
- Add, edit, delete, search, sort, and paginate books
- Add, edit, delete, search, sort, and paginate students
- Issue books with automatic available-copy reduction
- Return books with automatic available-copy increase
- Fine calculation at Rs. 5 per day after due date
- Overdue books list
- Issued, returned, overdue, and student-wise reports
- PDF and Excel report export
- Flash messages, validation, error pages, and responsive UI

## Installation Guide

1. Open a terminal in this folder:

```bash
cd library_management_system
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Initialize the database with sample data:

```bash
python database/init_db.py
```

6. Run the application:

```bash
python run.py
```

7. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Default Admin Login

```text
Username: admin
Password: admin123
```

## Database Tables

### Admin

- id
- username
- password

### Books

- id
- title
- author
- category
- isbn
- quantity
- available_quantity
- publication_year

### Students

- id
- name
- roll_number
- course
- email
- phone

### BookIssue

- id
- student_id
- book_id
- issue_date
- due_date
- return_date
- fine

## Project Notes

The application uses a modular MVC-style structure. SQLAlchemy models are defined in `models.py`, validation helpers are in `forms.py`, route blueprints are placed inside `routes/`, templates are grouped by module, and static files are separated into `static/css` and `static/js`.

For production use, change the `SECRET_KEY` in `config.py` or set it as an environment variable.
