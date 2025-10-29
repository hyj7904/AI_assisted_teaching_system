from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User  # 只导入User，不导入Class
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户已登录，重定向到对应面板
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        else:
            return redirect(url_for('teacher.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(phone=form.phone.data).first()

        # 检查用户是否存在且密码正确
        if user is None or not user.check_password(form.password.data):
            flash('手机号或密码错误', 'danger')
            return render_template('auth/login.html', form=form)

        # 登录用户
        login_user(user, remember=form.remember_me.data)
        flash('登录成功!', 'success')

        # 根据角色重定向
        next_page = request.args.get('next')
        if not next_page:
            if user.role == 'student':
                next_page = url_for('student.dashboard')
            else:
                next_page = url_for('teacher.dashboard')

        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    # 从URL参数获取角色
    role_from_url = request.args.get('role', 'student')
    if request.method == 'GET' and role_from_url in ['student', 'teacher']:
        form.role.data = role_from_url

    if form.validate_on_submit():
        # 检查手机号是否已存在
        existing_user = User.query.filter_by(phone=form.phone.data).first()
        if existing_user:
            flash('手机号已被注册', 'danger')
            return render_template('auth/register.html', form=form)

        # 创建新用户
        try:
            user = User(
                name=form.name.data,
                phone=form.phone.data,
                role=form.role.data
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash('注册成功! 请登录', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'注册失败: {str(e)}', 'danger')
            return render_template('auth/register.html', form=form)

    # 显示表单验证错误
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('index'))