from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import User, Post, Department, Dept_Locations, Employee, Project, Works_On, Dependent
from wtforms.fields.html5 import DateField


#  or could have used ssns = db.session.query(Department.mgr_ssn).distinct()
# for that way, we would have imported db from flaskDemo, see above
ssns = Department.query.with_entities(Department.mgr_ssn).distinct()
myChoices2 = [(row[0],row[0]) for row in ssns]  # change
results=list()
for row in ssns:
    rowDict=row._asdict()
    results.append(rowDict)
myChoices = [(row['mgr_ssn'],row['mgr_ssn']) for row in results]

essns = Employee.query.with_entities(Employee.ssn).distinct()
essnlist = []
for row in essns:
    rowDict=row._asdict()
    essnlist.append(rowDict)
essnchoices = [(row['ssn'],row['ssn']) for row in essnlist]

pnums = Project.query.with_entities(Project.pnumber).distinct()
pnumslist = []
for row in pnums:
    rowDict=row._asdict()
    pnumslist.append(rowDict)
pnumschoices = [(row['pnumber'], row['pnumber']) for row in pnumslist]

choices_add = []

triple = Employee.query.join(Works_On).join(Project).add_columns(Employee.ssn, Employee.dno, Employee.fname, Employee.lname, Project.plocation, Project.pname, Project.dnum, Project.pnumber, Works_On.pno, Works_On.essn, Works_On.hours)

regex1='^((((19|20)(([02468][048])|([13579][26]))-02-29))|((20[0-9][0-9])|(19[0-9][0-9]))-((((0[1-9])'
regex2='|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))$'
regex=regex1 + regex2


def Choices_add(pnumber):
    choices_add.clear()
    dnumber = Project.query.filter_by(pnumber = pnumber).first()
    dnumber = dnumber.dnum
    all = Employee.query.filter(Employee.dno == dnumber).distinct().all()
    for x in all:
        string = x.fname + " " + x.lname
        choices_add.append(string)
    choices_add = [(x, x) for x in choices_add]

def Choices_remove(pnumber):
    choices_add.clear()
    dnumber = Project.query.filter_by(pnumber = pnumber).first()
    dnumber = dnumber.dnum
    all = Employee.query.filter(Employee.dno == dnumber).distinct().all()
    for x in all:
        string = x.fname + " " + x.lname
        choices_add.append(string)
    choices_add = [(x, x) for x in choices_add]

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class DeptUpdateForm(FlaskForm):

#    dnumber=IntegerField('Department Number', validators=[DataRequired()])
    dnumber = HiddenField("")

    dname=StringField('Department Name:', validators=[DataRequired(),Length(max=15)])
#  Commented out using a text field, validated with a Regexp.  That also works, but a hassle to enter ssn.
#    mgr_ssn = StringField("Manager's SSN", validators=[DataRequired(),Regexp('^(?!000|666)[0-8][0-9]{2}(?!00)[0-9]{2}(?!0000)[0-9]{4}$', message="Please enter 9 digits for a social security.")])

#  One of many ways to use SelectField or QuerySelectField.  Lots of issues using those fields!!
    mgr_ssn = SelectField("Manager's SSN", choices=myChoices)  # myChoices defined at top

# the regexp works, and even gives an error message
#    mgr_start=DateField("Manager's Start Date:  yyyy-mm-dd",validators=[Regexp(regex)])
#    mgr_start = DateField("Manager's Start Date")

#    mgr_start=DateField("Manager's Start Date", format='%Y-%m-%d')
    mgr_start = DateField("Manager's start date:", format='%Y-%m-%d')  # This is using the html5 date picker (imported)
    submit = SubmitField('Update this department')


# got rid of def validate_dnumber

    def validate_dname(self, dname):    # apparently in the company DB, dname is specified as unique
         dept = Department.query.filter_by(dname=dname.data).first()
         if dept and (str(dept.dnumber) != str(self.dnumber.data)):
             raise ValidationError('That department name is already being used. Please choose a different name.')


class DeptForm(DeptUpdateForm):

    dnumber=IntegerField('Department Number', validators=[DataRequired()])
    submit = SubmitField('Add this department')

    def validate_dnumber(self, dnumber):    #because dnumber is primary key and should be unique
        dept = Department.query.filter_by(dnumber=dnumber.data).first()
        if dept:
            raise ValidationError('That department number is taken. Please choose a different one.')

class EmployeeUpdateForm(FlaskForm):

    #pnumber = SelectField("Project number", choices = pnumslist)
    #emp_ssn = SelectField("Employee's SSN", choices = essnchoices)
    submit = SubmitField('Update this Employee')


class EmplForm(EmployeeUpdateForm):
    essn = SelectField("Employee's Name", choices = choices_add)
    hours = IntegerField('Number of hours', validators=[DataRequired()])
    submit = SubmitField('Assign this Employee')

    #def validate_assignment(self, essn):    #because dnumber is primary key and should be unique
        #assign = Department.query.filter_by().first()
         #if employee in assign raise validation errpr

class removeEmplForm(EmployeeUpdateForm):
    essn = SelectField("Employee's Name", choices = choices_add)
    submit = SubmitField('Remove this Employee')
