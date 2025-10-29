from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, ClassInfo, Assignment, AssignmentSubmission, Exam, ExamQuestion, AssignmentQuestion
from forms import AssignmentForm, ExamForm, QuestionForm, ClassInfoForm
import json
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        flash('无权访问教师面板', 'danger')
        return redirect(url_for('index'))

    # 获取教师相关的统计信息
    classes = ClassInfo.query.all()
    assignments = Assignment.query.filter_by(teacher_id=current_user.id).all()
    exams = Exam.query.filter_by(teacher_id=current_user.id).all()

    return render_template('teacher/dashboard.html',
                           classes=classes,
                           assignments=assignments,
                           exams=exams)


@teacher_bp.route('/students')
@login_required
def students():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    students = User.query.filter_by(role='student').all()
    return render_template('teacher/students.html', students=students)


@teacher_bp.route('/classes')
@login_required
def classes():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    classes = ClassInfo.query.all()
    return render_template('teacher/classes.html', classes=classes)


@teacher_bp.route('/class/create', methods=['GET', 'POST'])
@login_required
def create_class():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    form = ClassInfoForm()

    if request.method == 'GET':
        form.major.choices = [('', '请先选择学院')]

    if form.validate_on_submit():
        existing_class = ClassInfo.query.filter_by(
            college=form.college.data,
            major=form.major.data,
            class_name=form.class_name.data
        ).first()

        if existing_class:
            flash('该班级已存在!', 'danger')
            return render_template('teacher/create_class.html', form=form)

        class_info = ClassInfo(
            college=form.college.data,
            major=form.major.data,
            class_name=form.class_name.data,
            description=form.description.data or f"{form.college.data}{form.major.data}{form.class_name.data}"
        )

        db.session.add(class_info)
        db.session.commit()

        flash('班级创建成功!', 'success')
        return redirect(url_for('teacher.classes'))

    return render_template('teacher/create_class.html', form=form)


@teacher_bp.route('/class/<int:class_id>/students')
@login_required
def class_students(class_id):
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    class_info = ClassInfo.query.get_or_404(class_id)
    students = User.query.filter_by(
        role='student',
        class_id=class_id
    ).order_by(User.student_id).all()

    return render_template('teacher/class_students.html',
                           class_info=class_info,
                           students=students)


@teacher_bp.route('/get_majors/<college>')
@login_required
def get_majors(college):
    if college == '计算机学院':
        majors = [
            {'id': '计算机科学与技术专业', 'name': '计算机科学与技术专业'},
            {'id': '物联网专业', 'name': '物联网专业'},
            {'id': '大数据专业', 'name': '大数据专业'}
        ]
    elif college == '人文学院':
        majors = [
            {'id': '汉语言专业', 'name': '汉语言专业'},
            {'id': '历史专业', 'name': '历史专业'}
        ]
    else:
        majors = []

    return jsonify({'majors': majors})


@teacher_bp.route('/assignment/create', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    form = AssignmentForm()
    form.class_id.choices = [(c.id, f"{c.college} - {c.major} - {c.class_name}") for c in ClassInfo.query.all()]

    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            class_id=form.class_id.data,
            teacher_id=current_user.id
        )
        db.session.add(assignment)
        db.session.commit()

        flash('作业创建成功!', 'success')
        return redirect(url_for('teacher.assignments'))  # 跳转到作业列表

    return render_template('teacher/create_assignment.html', form=form)


# 作业列表端点（已补充）
@teacher_bp.route('/assignments')
@login_required
def assignments():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    # 查询当前教师的所有作业，关联班级信息
    teacher_assignments = Assignment.query.filter_by(teacher_id=current_user.id)\
        .join(ClassInfo, Assignment.class_id == ClassInfo.id)\
        .add_columns(ClassInfo.college, ClassInfo.major, ClassInfo.class_name)\
        .order_by(Assignment.deadline.desc())\
        .all()

    return render_template('teacher/assignments.html', assignments=teacher_assignments)


@teacher_bp.route('/exam/create', methods=['GET', 'POST'])
@login_required
def create_exam():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    form = ExamForm()
    form.class_id.choices = [(c.id, f"{c.college} - {c.major} - {c.class_name}") for c in ClassInfo.query.all()]

    if form.validate_on_submit():
        exam = Exam(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            duration=form.duration.data,
            class_id=form.class_id.data,
            teacher_id=current_user.id
        )
        db.session.add(exam)
        db.session.commit()

        flash('考试创建成功!', 'success')
        return redirect(url_for('teacher.exam_questions', exam_id=exam.id))  # 保持原逻辑：跳转到添加题目

    return render_template('teacher/create_exam.html', form=form)


# 新增：考试列表端点（补充 teacher.exams）
@teacher_bp.route('/exams')
@login_required
def exams():
    if current_user.role != 'teacher':
        flash('无权访问此页面', 'danger')
        return redirect(url_for('index'))

    # 查询当前教师的所有考试，关联班级信息
    teacher_exams = Exam.query.filter_by(teacher_id=current_user.id)\
        .join(ClassInfo, Exam.class_id == ClassInfo.id)\
        .add_columns(ClassInfo.college, ClassInfo.major, ClassInfo.class_name)\
        .order_by(Exam.start_time.desc())\
        .all()

    return render_template('teacher/exams.html', exams=teacher_exams)


# 其他教师端路由（如 exam_questions 等）保持不变...