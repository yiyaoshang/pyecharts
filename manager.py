# -*- encoding=utf-8 -*-

from datamanager import app,db
from flask_script import Manager
from datamanager.models import User
import random
manager = Manager(app)

##创建数据库
@manager.command
def init_database():
    db.create_all()
    for i in range(0,100):
        db.session.add(User('User' + str(i),'a'+str(i)))
        for j in range(0,5):
            db.session.add(Image(get_image_url(),i+1))
            for k in range(0, 5):
                db.session.add(Comment('这是一条评论' + str(k), 1 + 5 * i + j, i + 1))
    db.session.commit()


##修改数据及删除数据
@manager.command
def update_database():
    for i in range(0, 100, 10):
        # 通过update函数
        User.query.filter_by(id=i + 1).update({'username': 'new' + str(i)})

    for i in range(1, 100, 2):
        # 通过设置属性
        u = User.query.get(i + 1)
        u.username = 'd' + str(i * i)
    db.session.commit()

    # 删除
    for i in range(50, 100, 2):
        Comment.query.filter_by(id=i + 1).delete()
    for i in range(51, 100, 2):
        comment = Comment.query.get(i + 1)
        db.session.delete(comment)
    db.session.commit()


#查询数据
@manager.command
def show_database():
    #print 1, User.query.all()
    #print 2, User.query.get(3)  # primary key = 3
    #print 3, User.query.filter_by(id=2).first()
    #print 4, User.query.order_by(User.id.desc()).offset(1).limit(2).all()
    print 4,Image.query.order_by(db.desc(Image.id)).limit(10).all()
    #print 5, User.query.paginate(page=1, per_page=10).items
    #u = User.query.get(1)
    #print 6, u
    #print 7, u.images
    #print 8, Image.query.get(1).user


if __name__ == '__main__':
    manager.run()
