from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models import Admin, db


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.dashboard import dashboard_bp
    from routes.issues import issues_bp
    from routes.reports import reports_bp
    from routes.students import students_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(issues_bp, url_prefix="/issues")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


if __name__ == "__main__":
    create_app().run(debug=True)
