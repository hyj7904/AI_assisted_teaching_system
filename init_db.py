from app import app
from extensions import db
from models import User, ClassInfo
from datetime import datetime


def init_database():
    with app.app_context():
        # 删除所有表并重新创建
        db.drop_all()
        db.create_all()

        print("创建表结构...")

        # 创建示例班级
        '''
        print("添加示例班级...")
        class1 = ClassInfo(
            college='计算机学院',
            major='计算机科学与技术专业',
            class_name='1班',
            description='计算机科学与技术专业1班'
        )

        class2 = ClassInfo(
            college='计算机学院',
            major='物联网专业',
            class_name='1班',
            description='物联网专业1班'
        )

        class3 = ClassInfo(
            college='人文学院',
            major='汉语言专业',
            class_name='1班',
            description='汉语言专业1班'
        )

        db.session.add(class1)
        db.session.add(class2)
        db.session.add(class3)
        db.session.commit()
        '''

        # 创建示例教师
        print("添加示例教师...")
        teacher1 = User(
            name='张老师',
            phone='13800138001',
            role='teacher'
        )
        teacher1.set_password('password123')

        teacher2 = User(
            name='李老师',
            phone='13800138002',
            role='teacher'
        )
        teacher2.set_password('password123')

        db.session.add(teacher1)
        db.session.add(teacher2)
        db.session.commit()

        # 创建示例学生
        print("添加示例学生...")

        student1 = User(
            name='张三',
            phone='13800138003',
            role='student',
            student_id='2021001',
            class_id=1  # 关联到计算机科学与技术1班
        )
        student1.set_password('password123')

        student2 = User(
            name='李四',
            phone='13800138004',
            role='student',
            student_id='2021002',
            class_id=2  # 关联到物联网1班
        )
        student2.set_password('password123')

        student3 = User(
            name='王五',
            phone='13800138005',
            role='student',
            student_id='2021003',
            class_id=3  # 关联到汉语言1班
        )
        student3.set_password('password123')

        db.session.add(student1)
        db.session.add(student2)
        db.session.add(student3)
        db.session.commit()

        print("数据库初始化完成!")
        '''
        print("\n可用的测试账号:")
        print("教师账号: 13800138001 / password123 (张老师)")
        print("教师账号: 13800138002 / password123 (李老师)")
        print("学生账号: 13800138003 / password123 (张三)")
        print("学生账号: 13800138004 / password123 (李四)")
        print("学生账号: 13800138005 / password123 (王五)")
        '''


if __name__ == '__main__':
    init_database()
