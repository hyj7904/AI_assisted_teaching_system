from flask import Flask, render_template
import os
from extensions import db, login_manager

app = Flask(__name__)
app.config.from_object('config.Config')

# 初始化数据库
db.init_app(app)

# 初始化登录管理
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'warning'

# 创建上传目录
os.makedirs('static/uploads/assignments', exist_ok=True)
os.makedirs('static/uploads/word_files', exist_ok=True)

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# 注册蓝图
from routes.auth import auth_bp
from routes.student import student_bp
from routes.teacher import teacher_bp

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)