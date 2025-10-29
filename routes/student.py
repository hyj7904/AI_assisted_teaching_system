from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Assignment, AssignmentSubmission, Exam, ExamSubmission, ClassInfo, User
from forms import AssignmentSubmissionForm, StudentProfileForm
import os
from datetime import datetime
from models import User  # 假设User模型有college、major、class_id字段
from forms import StudentInfoForm


student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    # 获取学生的作业和考试信息
    assignments = Assignment.query.filter_by(class_id=current_user.class_id).all()
    exams = Exam.query.filter_by(class_id=current_user.class_id).all()

    return render_template('student/dashboard.html',
                           assignments=assignments,
                           exams=exams)


@student_bp.route('/assignments')
@login_required
def assignments():
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    assignments = Assignment.query.filter_by(class_id=current_user.class_id).all()
    return render_template('student/assignments.html', assignments=assignments)


@student_bp.route('/assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def assignment_detail(assignment_id):
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    assignment = Assignment.query.get_or_404(assignment_id)
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=current_user.id
    ).first()

    form = AssignmentSubmissionForm()
    if form.validate_on_submit():
        # 处理文件上传
        file_path = None
        if form.file.data:
            filename = f"assignment_{assignment_id}_student_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
            file_path = os.path.join('static/uploads/assignments', filename)
            form.file.data.save(file_path)

        if submission:
            # 更新现有提交
            submission.text_answer = form.text_answer.data
            submission.file_path = file_path if file_path else submission.file_path
            submission.submitted_at = datetime.utcnow()
            submission.graded = False
            flash('作业已更新!', 'success')
        else:
            # 创建新提交
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                text_answer=form.text_answer.data,
                file_path=file_path,
                submitted_at=datetime.utcnow()
            )
            db.session.add(submission)
            flash('作业提交成功!', 'success')

        db.session.commit()
        return redirect(url_for('student.assignment_detail', assignment_id=assignment_id))

    return render_template('student/assignment_detail.html',
                           assignment=assignment,
                           submission=submission,
                           form=form)


@student_bp.route('/grades')
@login_required
def grades():
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    submissions = AssignmentSubmission.query.filter_by(
        student_id=current_user.id
    ).join(Assignment).all()

    return render_template('student/grades.html', submissions=submissions)


@student_bp.route('/exams')
@login_required
def exams():
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    exams = Exam.query.filter_by(class_id=current_user.class_id).all()
    return render_template('student/exams.html', exams=exams)


@student_bp.route('/exam/<int:exam_id>')
@login_required
def exam_detail(exam_id):
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    exam = Exam.query.get_or_404(exam_id)
    return render_template('student/exam_detail.html', exam=exam)


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        flash('无权访问学生面板', 'danger')
        return redirect(url_for('index'))

    form = StudentProfileForm()

    # 设置专业选项的初始值
    if current_user.class_info and current_user.class_info.college:
        form.college.data = current_user.class_info.college
        if current_user.class_info.college == '计算机学院':
            form.major.choices = [
                ('', '请选择专业'),
                ('计算机科学与技术专业', '计算机科学与技术专业'),
                ('物联网专业', '物联网专业'),
                ('大数据专业', '大数据专业')
            ]
        else:
            form.major.choices = [
                ('', '请选择专业'),
                ('汉语言专业', '汉语言专业'),
                ('历史专业', '历史专业')
            ]
        form.major.data = current_user.class_info.major if current_user.class_info else ''
    else:
        form.college.data = ''
        form.major.choices = [('', '请先选择学院')]

    # 设置班级选项
    form.class_name.choices = [
        ('', '请选择班级'),
        ('1班', '1班'),
        ('2班', '2班'),
        ('3班', '3班')
    ]

    # 设置表单初始值
    if request.method == 'GET':
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.student_id.data = current_user.student_id

        if current_user.class_info:
            form.college.data = current_user.class_info.college
            form.major.data = current_user.class_info.major
            form.class_name.data = current_user.class_info.class_name

    # 设置用户ID用于验证
    form.set_user_id(current_user.id)

    if form.validate_on_submit():
        # 查找或创建班级
        class_info = ClassInfo.query.filter_by(
            college=form.college.data,
            major=form.major.data,
            class_name=form.class_name.data
        ).first()

        if not class_info:
            # 创建新班级
            class_info = ClassInfo(
                college=form.college.data,
                major=form.major.data,
                class_name=form.class_name.data,
                description=f"{form.college.data}{form.major.data}{form.class_name.data}"
            )
            db.session.add(class_info)
            db.session.flush()  # 获取ID但不提交事务

        # 更新用户信息
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.student_id = form.student_id.data
        current_user.class_id = class_info.id

        try:
            db.session.commit()
            flash('个人信息更新成功!', 'success')
            return redirect(url_for('student.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('student/profile.html', form=form)


# 学生个人中心-信息修改页面
@student_bp.route('/profile/info', methods=['GET', 'POST'])
@login_required
def edit_info():
    if current_user.role != 'student':
        flash('无权访问学生个人中心', 'danger')
        return redirect(url_for('index'))

    form = StudentInfoForm()
    # GET请求：初始化表单为当前用户信息
    if request.method == 'GET':
        # 回显当前学院、专业
        form.college.data = current_user.college
        form.major.data = current_user.major
        # 班级选项需关联ClassInfo（根据当前班级ID回显）
        if current_user.class_id:
            form.class_id.choices = [
                (c.id, c.class_name) for c in ClassInfo.query.filter_by(
                    college=current_user.college,
                    major=current_user.major
                ).all()
            ]
            form.class_id.data = current_user.class_id

    # POST请求：处理修改提交
    if form.validate_on_submit():
        # 验证学院、专业、班级是否匹配（防止前端篡改数据）
        college = form.college.data
        major = form.major.data
        class_id = form.class_id.data

        # 检查班级是否属于所选学院和专业
        class_info = ClassInfo.query.filter_by(
            id=class_id,
            college=college,
            major=major
        ).first()
        if not class_info:
            flash('所选班级与学院/专业不匹配', 'danger')
            return render_template('student/edit_info.html', form=form)

        # 更新用户信息
        current_user.college = college
        current_user.major = major
        current_user.class_id = class_id

        try:
            db.session.commit()
            flash('学院、专业、班级修改成功', 'success')
            return redirect(url_for('student.edit_info'))  # 重定向刷新页面
        except Exception as e:
            db.session.rollback()
            flash(f'修改失败：{str(e)}', 'danger')

    return render_template('student/edit_info.html', form=form)


# 动态加载专业（根据学院）
@student_bp.route('/get_majors/<college>')
@login_required
def get_majors(college):
    if current_user.role != 'student':
        return jsonify({'majors': []}), 403  # 拒绝非学生访问

    # 与教师创建班级时的专业逻辑保持一致（可抽为公共函数）
    if college == '计算机学院':
        majors = [{'id': '计算机科学与技术专业', 'name': '计算机科学与技术专业'},
                  {'id': '物联网专业', 'name': '物联网专业'},
                  {'id': '大数据专业', 'name': '大数据专业'}]
    elif college == '人文学院':
        majors = [{'id': '汉语言专业', 'name': '汉语言专业'},
                  {'id': '历史专业', 'name': '历史专业'}]
    else:
        majors = []
    return jsonify({'majors': majors})


# 动态加载班级（根据学院和专业）
@student_bp.route('/get_classes/<college>/<major>')
@login_required
def get_classes(college, major):
    if current_user.role != 'student':
        return jsonify({'classes': []}), 403  # 拒绝非学生访问

    # 从ClassInfo中查询对应学院和专业的班级
    classes = ClassInfo.query.filter_by(college=college, major=major).all()
    class_list = [{'id': c.id, 'name': c.class_name} for c in classes]
    return jsonify({'classes': class_list})