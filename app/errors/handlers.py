from flask import render_template
from app import app, db
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
#
# @bp.app_errorhandler(Exception)                     #TODO logging + HTTP exceptions in order to keep the error code
# def internal_error(error):
#     db.session.rollback()
#     return render_template('errors/500.html'), 500

