import os
from flask import Flask

def create_app(test_config= None):

    app = Flask(__name__, instance_relative_config= True)
    app.config.from_mapping(
        SECRET_KEY = 'dEV', 
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent= True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr import db
    db.init_app(app)

    from flaskr import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule('/', endpoint='login')

    return app
