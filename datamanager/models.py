# -*- encoding=utf-8 -*-

from datamanager import db,login_manager
import  random
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comment'
    #__table_args__ = {'mysql_collate': 'utf-8'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)
    user = db.relationship('User')

    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return ('<Comment%d %s>' % (self.id, self.content))


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    def __init__(self,url,user_id):
        self.url = url
        self.user_id = user_id
        self.create_date = datetime.now()

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(80),unique=True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    images = db.relationship('Image', backref='user', lazy='dynamic')

    def __init__(self, username, passworld,salt = ''):
        self.username = username
        self.password = passworld
        self.salt = salt
        self.head_url = '../static/touxiang/' + str(random.randint(0,127)) + '.jpg'

    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)


    # Flask Login接口
    def is_authenticated(self):
        print 'is_authenticated'
        return True


    def is_active(self):
        print 'is_active'
        return True


    def is_anonymous(self):
        print 'is_anonymous'
        return False


    def get_id(self):
        print 'get_id'
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
