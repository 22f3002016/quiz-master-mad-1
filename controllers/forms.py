from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, IntegerField, SelectField, SubmitField, RadioField,BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.widgets import HiddenInput
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Subject')

class ChapterForm(FlaskForm):
    name = StringField('Chapter Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Chapter')

class QuizForm(FlaskForm):
    name = StringField('Quiz Name', validators=[DataRequired()])
    date_of_quiz = DateField('Date of Quiz', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now())
    time_duration = IntegerField('Time Duration (minutes)', validators=[DataRequired()], default=30)
    chapter_id = SelectField('Chapter', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Quiz')

class QuestionForm(FlaskForm):
    question_statement = TextAreaField('Question', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_option = RadioField('Correct Option', choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')], coerce=int, validators=[DataRequired()])
    quiz_id = SelectField('Quiz', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Question')

class QuizAttemptForm(FlaskForm):
    submit = SubmitField('Submit Quiz')

class QuestionAnswerForm(FlaskForm):
    question_id = IntegerField(widget=HiddenInput())
    selected_option = RadioField('Select Answer', choices=[(1, ''), (2, ''), (3, ''), (4, '')], coerce=int)


