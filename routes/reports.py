from datetime import date
from io import BytesIO

from flask import Blueprint, Response, make_response, render_template, request
from flask_login import login_required

from models import BookIssue, Student


reports_bp = Blueprint("reports", __name__)


def report_query(report_type, student_id=None):
    query = BookIssue.query
    if report_type == "returned":
        query = query.filter(BookIssue.return_date.isnot(None))
    elif report_type == "overdue":
        query = query.filter(BookIssue.return_date.is_(None), BookIssue.due_date < date.today())
    elif report_type == "student" and student_id:
        query = query.filter(BookIssue.student_id == student_id)
    else:
        query = query.filter(BookIssue.return_date.is_(None))
    return query.order_by(BookIssue.issue_date.desc()).all()


@reports_bp.route("/")
@login_required
def index():
    report_type = request.args.get("type", "issued")
    student_id = request.args.get("student_id", type=int)
    students = Student.query.order_by(Student.name).all()
    issues = report_query(report_type, student_id)
    return render_template("reports/index.html", issues=issues, students=students, report_type=report_type, student_id=student_id)


@reports_bp.route("/export/excel")
@login_required
def export_excel():
    from openpyxl import Workbook

    report_type = request.args.get("type", "issued")
    student_id = request.args.get("student_id", type=int)
    wb = Workbook()
    ws = wb.active
    ws.title = "Library Report"
    ws.append(["Issue ID", "Student", "Roll No", "Book", "ISBN", "Issue Date", "Due Date", "Return Date", "Fine"])

    for issue in report_query(report_type, student_id):
        ws.append([
            issue.id,
            issue.student.name,
            issue.student.roll_number,
            issue.book.title,
            issue.book.isbn,
            issue.issue_date.isoformat(),
            issue.due_date.isoformat(),
            issue.return_date.isoformat() if issue.return_date else "",
            issue.calculate_fine() if not issue.return_date else issue.fine,
        ])

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    response = make_response(file_stream.read())
    response.headers["Content-Disposition"] = f"attachment; filename={report_type}_books_report.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    report_type = request.args.get("type", "issued")
    student_id = request.args.get("student_id", type=int)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    rows = [["ID", "Student", "Roll", "Book", "Issue", "Due", "Return", "Fine"]]

    for issue in report_query(report_type, student_id):
        rows.append([
            issue.id,
            issue.student.name,
            issue.student.roll_number,
            issue.book.title,
            issue.issue_date.isoformat(),
            issue.due_date.isoformat(),
            issue.return_date.isoformat() if issue.return_date else "-",
            f"Rs. {issue.calculate_fine() if not issue.return_date else issue.fine:.2f}",
        ])

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
    ]))
    doc.build([table])
    buffer.seek(0)
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={report_type}_books_report.pdf"},
    )
