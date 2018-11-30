from flaskr.db import get_db
from flask import (Blueprint, redirect, flash, render_template, g, url_for, request)
from werkzeug.exceptions import abort
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

@bp.route('/index')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u'
        ' ON p.author_id=u.id WHERE p.author_id=? ORDER BY created DESC', (g.user['id'],)
        ).fetchall()
    return render_template('blog/index.html', posts=posts)

def get_post(id, check_author=True):
    db = get_db()
    post = db.execute(
        'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u'
        ' ON p.author_id=u.id WHERE p.id=?', (id,)
        ).fetchone()

    if post is None:
        abort(404, "post id {0} doesn't exist".format(id))
    elif check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if title is None:
            error = 'Title is required!'
        
        if error is not None:
            flash(error)

        db = get_db()
        db.execute('INSERT INTO post(title, body, author_id)'
            ' VALUES(?, ?, ?)',(title, body, g.user['id'],))
        db.commit()

        return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=['GET','POST'])
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if title is None:
            error = 'Title is required!'
        
        if error is not None:
            flash(error)

        db = get_db()
        db.execute('UPDATE post SET title=?, body=? WHERE id=?',(title, body, id))
        db.commit()

        return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    get_post(id) #确保要删除的博客存在
    db = get_db()
    db.execute('DELETE FROM post WHERE id=?',(id,))
    db.commit()
    return redirect(url_for('blog.index'))
