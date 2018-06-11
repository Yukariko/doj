from flask_login import UserMixin
from flask_security import RoleMixin, current_user
from flask.json import dumps
from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from app.search import add_to_index, remove_from_index, query_index
from flask_admin.contrib import sqla

followers = db.Table(
                'followers',
                db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
            )

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total
        
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }
    
    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
            
        session.changes = None
    
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model, RoleMixin):
    id          = db.Column(db.Integer(), primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

class User(UserMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(64), index=True, unique=True)
    email       = db.Column(db.String(120), index=True, unique=True)
    password    = db.Column(db.String(128))
    about_me    = db.Column(db.String(140))
    active      = db.Column(db.Boolean())
    last_seen   = db.Column(db.DateTime, default=datetime.utcnow)
    roles       = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    posts       = db.relationship('Post', backref='author', lazy='dynamic')
    problems    = db.relationship('Problem', backref='author', lazy='dynamic')
    submits     = db.relationship('Submit', backref='submitor', lazy='dynamic')
    followed    = db.relationship(
                    'User',
                    secondary = followers,
                    primaryjoin = (followers.c.follower_id == id),
                    secondaryjoin = (followers.c.followed_id == id),
                    backref = db.backref('followers', lazy = 'dynamic'),
                    lazy = 'dynamic'
                  )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers,
            (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def has_role(self, role):
        role = Role.query.filter_by(name = role).first()
        return self in role.users

class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.String(140))
    timestamp   = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

# 문제는 공개, 비공개, 일부공개등 다양한 상태가 있을 예정
class Problem(SearchableMixin, db.Model):
    __searchable__  = ['title']
    id              = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(200))
    body            = db.Column(db.Text)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_limit      = db.Column(db.Integer)
    memory_limit    = db.Column(db.Integer)
    submits         = db.relationship('Submit', backref='problem', lazy='dynamic')

class ProblemContent(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    problem_id      = db.Column(db.Integer, db.ForeignKey('problem.id'))
    input           = db.Column(db.Text)
    output          = db.Column(db.Text)

class Language(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(30))
    compile_command = db.Column(db.String(200))
    submits         = db.relationship('Submit', backref='language', lazy='dynamic')

class Result(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(30))
    submits         = db.relationship('Submit', backref='result', lazy='dynamic')

class Submit(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    problem_id      = db.Column(db.Integer, db.ForeignKey('problem.id'))
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'))
    language_id     = db.Column(db.Integer, db.ForeignKey('language.id'))
    result_id       = db.Column(db.Integer, db.ForeignKey('result.id'))
    spend_time      = db.Column(db.Integer)
    spend_memory    = db.Column(db.Integer)
    timestamp       = db.Column(db.DateTime, default=datetime.utcnow)
    code            = db.Column(db.Text)
    byte            = db.Column(db.Integer)
    accessable      = db.Column(db.Integer)