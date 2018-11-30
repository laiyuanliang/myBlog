import functools
from flask import (Blueprint, flash, request, render_template, session, url_for, g, redirect)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db 

bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('select * from user where id=?',(user_id,)).fetchone()

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'
        elif db.execute('select * from user where username=?', (username,)).fetchone() is not None:
            error = 'User {0} already exist!'.format(username)

        if error is None:
            db.execute('insert into user(username, password) values(?, ?)',(username, generate_password_hash(password),))
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute('select * from user where username=?', (username,)).fetchone()
        if user is None:
            error = "User {0} doesn't exist!".format(username)
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password!'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/reset', methods=['GET','POST'])
def reset():
    if request.method == 'POST':
        username = request.form['username']
        OriginalPassword = request.form['OriginalPassword']
        NewPassword1 = request.form['NewPassword1']
        NewPassword2 = request.form['NewPassword2']
        db = get_db()
        error = None

        user = db.execute('select * from user where username=?', (username,)).fetchone()
        if user is None:
            error = "User {0} doesn't exist!".format(username)
        elif not check_password_hash(user['password'], OriginalPassword):
            error = 'Incorrect original password!'
        elif NewPassword1 != NewPassword2:
            error = "You have submit 2 different password, please try again!"

        if error is None:
            db.execute('UPDATE user SET password=? WHERE username=?', (generate_password_hash(NewPassword1), username))
            db.commit()
            flash("Password for {0} has been reset successfully!".format(username))
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/reset_password.html')

@bp.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('login'))
