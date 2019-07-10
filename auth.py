import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from talkdict.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# When Flask receives a request to /auth/register, it will call the register view and use the return value as the response.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'User {username} is already registered.'

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)', 
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        # flash() stores messages that can be retrieved when rendering the template
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Username not found.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data "across requests"
            session.clear()
            session['user_id'] = user['id']
            # Now that the user’s id is stored in the session, it will be available on subsequent requests.
            current_app.logger.info('redirect to index')
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

# bp.before_app_request() registers a function that executes before each request, no matter what URL is requested, even if outside of a blueprint.. 
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    current_app.logger.debug('In load_logged_in_user')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        current_app.logger.info('load_logged_in_user')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# The new function checks if a user is loaded and redirects to the login page otherwise. If a user is loaded the original view is called and continues normally. 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
    


