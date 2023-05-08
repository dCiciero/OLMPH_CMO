from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found(error):
    """Page not found."""
    return render_template("app/404.html"), 404


# @app.errorhandler(400)
# def bad_request():
#     """Bad request."""
#     return render_template("app/400.html"), 400


@app.errorhandler(500)
def server_error(error):
    """Internal server error."""
    db.session.rollback()
    return render_template("app/500.html"), 500