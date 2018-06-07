from flask import Flask
from flask import render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore
from elasticsearch import Elasticsearch
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()
moment = Moment()

from app.models import User, Language, Result, Role, MyModelView, Submit

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

def create_app(config_class=Config):
    app = Flask(__name__)
    security = Security(app, user_datastore)
    admin = Admin(app, name='doj', base_template='base.html', template_mode='bootstrap3')
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Language, db.session))
    admin.add_view(MyModelView(Result, db.session))
    admin.add_view(MyModelView(Role, db.session))
    admin.add_view(MyModelView(Submit, db.session))

    app.config.from_object(config_class)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.problem import bp as problem_bp
    app.register_blueprint(problem_bp, url_prefix='/problem')

    return app

from app import models
