# 定义数据库模型

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10))  # 'student' or 'teacher'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    students = db.relationship('User', backref='class_ref', lazy='dynamic')

# 其他模型类似，根据上述设计创建

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))