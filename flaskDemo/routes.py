import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, DeptForm,DeptUpdateForm, EmplForm, EmployeeUpdateForm, removeEmplForm
from flaskDemo.forms import *
from flaskDemo.models import User, Post,Department, Dependent, Dept_Locations, Employee, Project, Works_On
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
    results = Department.query.all()
    return render_template('dept_home.html', outString = results)
    posts = Post.query.all()
    return render_template('home.html', posts=posts)
    results2 = Faculty.query.join(Qualified,Faculty.facultyID == Qualified.facultyID) \
               .add_columns(Faculty.facultyID, Faculty.facultyName, Qualified.Datequalified, Qualified.courseID) \
               .join(Course, Course.courseID == Qualified.courseID).add_columns(Course.courseName)
    results = Faculty.query.join(Qualified,Faculty.facultyID == Qualified.facultyID) \
              .add_columns(Faculty.facultyID, Faculty.facultyName, Qualified.Datequalified, Qualified.courseID)
    return render_template('join.html', title='Join',joined_1_n=results, joined_m_n=results2)




@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/dept/new", methods=['GET', 'POST'])
@login_required
def new_dept():
    form = DeptForm()
    if form.validate_on_submit():
        dept = Department(dname=form.dname.data, dnumber=form.dnumber.data,mgr_ssn=form.mgr_ssn.data,mgr_start=form.mgr_start.data)
        db.session.add(dept)
        db.session.commit()
        flash('You have added a new department!', 'success')
        return redirect(url_for('home'))
    return render_template('create_dept.html', title='New Department',
                           form=form, legend='New Department')


@app.route("/dept/<dnumber>")
@login_required
def dept(dnumber):
    #get dept
    dept = Department.query.get_or_404(dnumber)
    #get projects list that match department
    projs = Project.query.filter_by(dnum = dnumber).all()
    projlist = []
    #iterate through all projects so that we can get the employees meant for each project
    for proj in projs:
        #THIS WAS THE ISSUE
        #The query at the top of this .py 'triple' was the issue since it was not refreshing each time dept is refreshed.  
        empls= Employee.query.join(Works_On).filter_by(pno = proj.pnumber).all()
        emplist = []
        for emp in empls:
            emplist.append(emp)
        #a 3 dimensional list is probably not the best way
        projlist.extend([[proj, emplist]])
    print(projlist)
    return render_template('dept.html', title=dept.dname, dept=dept, projlist = projlist, now = datetime.utcnow())



@app.route("/dept/<dnumber>/update", methods=['GET', 'POST'])
@login_required
def update_dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    currentDept = dept.dname
    form = DeptUpdateForm()
    if form.validate_on_submit():          # notice we are are not passing the dnumber from the form
        if currentDept !=form.dname.data:
            dept.dname=form.dname.data
        dept.mgr_ssn=form.mgr_ssn.data
        dept.mgr_start=form.mgr_start.data
        db.session.commit()
        flash('Your department has been updated!', 'success')
        return redirect(url_for('dept', dnumber=dnumber))
    elif request.method == 'GET':              # notice we are not passing the dnumber to the form
        form.dnumber.data = dept.dnumber
        form.dname.data = dept.dname
        form.mgr_ssn.data = dept.mgr_ssn
        form.mgr_start.data = dept.mgr_start
    return render_template('create_dept.html', title='Update Department',
                           form=form, legend='Update Department')




@app.route("/dept/<dnumber>/delete", methods=['POST'])
@login_required
def delete_dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    db.session.delete(dept)
    db.session.commit()
    flash('The department has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/empl/<pnumber>/new_assignment", methods=['GET', 'POST'])
@login_required
def new_empl_assign(pnumber):
    #function is in forms - but was struggling with adding the correct choices to the drop down box
    Choices_add(pnumber)
    #form
    form = EmplForm()
    if form.validate_on_submit():
        #get First Last, used first name to get the ssn so that works_on can be updated
        name = str(form.essn.data)
            #splits string into list
        name = name.split()
            #use first element
        name = name[0]
            #now query
        essn = Employee.query.filter_by(fname = name).first()
            #add and commit
        empl = Works_On(pno = pnumber, essn = essn.ssn, hours = form.hours.data)
        db.session.add(empl)
        db.session.commit()
        flash('You have added a new employee assignment!', 'success')
        return redirect(url_for('home'))
    return render_template('create_empl.html', title='New Employee Assignment',
                           form = form, legend='New Employee Assignment')

@app.route("/empl/<pnumber>/remove", methods=['GET', 'POST'])
@login_required
def remove_empl_assign(pnumber):
    #function is in forms - but was struggling with adding the correct choices to the drop down box
    Choices_remove(pnumber)
    form = removeEmplForm()
    if form.validate_on_submit():
        ##get First Last, used first name to get the ssn so that works_on can be updated
        name = str(form.essn.data)
        name = name.split()
        name = name[0]
        essn = Employee.query.filter_by(fname = name).first()
        empl = Works_On.query.filter_by(essn = essn.ssn, pno = pnumber).first()
        db.session.delete(empl)
        db.session.commit()
        flash('You have removed an employee assignment!', 'danger')
        return redirect(url_for('home'))
    return render_template('reassign_empl.html', title='Remove Employee Assignment',
                           form = form, legend='Remove Employee Assignment')
