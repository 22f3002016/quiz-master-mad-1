from datetime import datetime
from controllers import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String)
    dob = db.Column(db.Date)

    # Cascade delete applied to prevent integrity errors
    scores = db.relationship('Score', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Cascade delete to handle dependent chapters
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_quiz = db.Column(db.DateTime)
    time_duration = db.Column(db.Integer, default=0)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    total_questions = db.Column(db.Integer, default=0)  

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")

    def update_question_count(self):
        self.total_questions = len(self.questions)
        db.session.commit()

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.Text)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_scored = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False, default=0)