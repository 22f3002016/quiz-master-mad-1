from controllers import app, db, login_manager
from flask import render_template, redirect, flash, url_for, request, jsonify
from controllers.forms import RegisterForm, LoginForm, SubjectForm, ChapterForm, QuizForm, QuestionForm, QuizAttemptForm, QuestionAnswerForm
from models.models import User, Subject, Chapter, Quiz, Question, Score 
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
from controllers.forms import UserSearchForm, AdminSearchForm
from flask_wtf.csrf import generate_csrf 
from io import BytesIO
import base64
import matplotlib 
import matplotlib.pyplot as plt
from sqlalchemy import func



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command("db-create")
def create_db():
    with app.app_context():
        db.create_all()
        

        admin = User.query.filter_by(username="admin@quizmaster.com").first()
        if not admin:
            admin = User(
                username="admin@quizmaster.com",
                fullname="Quiz Master Admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("admin created")
        else:
            print("admin already there")
        print("database created")
    
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            fullname=form.fullname.data,
            qualification=form.qualification.data,
            dob=form.dob.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You were successfully registered', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.username == "admin@quizmaster.com":
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            if user.username == "admin@quizmaster.com":
                flash("Admin login successful", 'success')
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        flash("Invalid username or password", 'danger')
        
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        # Get recent scores with question count from the score record itself
        recent_scores = Score.query.filter_by(user_id=current_user.id)\
            .order_by(Score.timestamp.desc())\
            .limit(5)\
            .all()

        quizzes = Quiz.query.join(Chapter).join(Subject).with_entities(
            Quiz.id, Quiz.name, Quiz.date_of_quiz, Quiz.time_duration,
            Chapter.name.label('chapter_name'), Subject.name.label('subject_name')
        ).all()
        
        # Serialize recent scores using the stored total_questions
        recent_scores_data = [
            {
                'quiz_name': score.quiz.name if score.quiz else "Unknown Quiz",
                'total_scored': score.total_scored or 0,
                'questions_count': score.total_questions or 1,
                'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M:%S') if score.timestamp else "Unknown"
            }
            for score in recent_scores
        ]

        # Calculate score distribution using the stored total_questions
        all_scores = Score.query.filter_by(user_id=current_user.id).all()
        score_distribution = {'0-25': 0, '26-50': 0, '51-75': 0, '76-100': 0}

        for score in all_scores:
            if score.total_questions and score.total_questions > 0:
                percentage = (score.total_scored / score.total_questions) * 100
                if percentage <= 25:
                    score_distribution['0-25'] += 1
                elif percentage <= 50:
                    score_distribution['26-50'] += 1
                elif percentage <= 75:
                    score_distribution['51-75'] += 1
                else:
                    score_distribution['76-100'] += 1

        return render_template("dashboard.html", 
                              user=current_user, 
                              recent_scores=recent_scores_data, 
                              quizzes=quizzes,
                              score_distribution=score_distribution)
    except Exception as e:
        # Add proper error handling here
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('home'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route("/admin/dashboard") 
@login_required
def admin_dashboard():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    subject_count = Subject.query.count()
    chapter_count = Chapter.query.count()
    quiz_count = Quiz.query.count()
    question_count = Question.query.count()
    user_count = User.query.count() - 1  
    score_count = Score.query.count()
    
    return render_template("admin/dashboard.html", 
                          subject_count=subject_count,
                          chapter_count=chapter_count,
                          quiz_count=quiz_count,
                          question_count=question_count,
                          user_count=user_count,
                          score_count=score_count)

@app.route("/admin/manage_subjects", methods=['GET', 'POST'])
@login_required
def admin_manage_subjects():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully', 'success')
        return redirect(url_for('admin_manage_subjects'))
    
    subjects = Subject.query.all()
    return render_template("admin/manage_subjects.html", subjects=subjects, form=form)

@app.route("/admin/edit_subject/<int:subject_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_subject(subject_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash('Subject updated successfully', 'success')
        return redirect(url_for('admin_manage_subjects'))
    
    return render_template('admin/edit_subject.html', form=form, subject=subject)

@app.route("/admin/delete_subject/<int:subject_id>", methods=['POST'])
@login_required
def admin_delete_subject(subject_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('admin_manage_subjects'))

@app.route("/admin/manage_chapters", methods=['GET', 'POST'])
@login_required
def admin_manage_chapters():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    form = ChapterForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=form.subject_id.data
        )
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter created successfully', 'success')
        return redirect(url_for('admin_manage_chapters'))
    
    chapters = Chapter.query.join(Subject).with_entities(
        Chapter.id, Chapter.name, Chapter.description, Subject.name.label('subject_name')
    ).all()
    
    return render_template("admin/manage_chapters.html", chapters=chapters, form=form)

@app.route("/admin/edit_chapter/<int:chapter_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_chapter(chapter_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    form = ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('admin_manage_chapters'))
    
    return render_template('admin/edit_chapter.html', form=form, chapter=chapter)

@app.route("/admin/delete_chapter/<int:chapter_id>", methods=['POST'])
@login_required
def admin_delete_chapter(chapter_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('admin_manage_chapters'))

@app.route("/admin/manage_quizzes", methods=['GET', 'POST'])
@login_required
def admin_manage_quizzes():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    form = QuizForm()
    form.chapter_id.choices = [(c.id, f"{c.name} ({Subject.query.get(c.subject_id).name})") 
                              for c in Chapter.query.all()]
    
    if form.validate_on_submit():
        quiz = Quiz(
            name=form.name.data,
            date_of_quiz=form.date_of_quiz.data,
            time_duration=form.time_duration.data,
            chapter_id=form.chapter_id.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully', 'success')
        return redirect(url_for('admin_manage_quizzes'))
    
    quizzes = Quiz.query.join(Chapter).join(Subject).with_entities(
        Quiz.id, Quiz.name, Quiz.date_of_quiz, Quiz.time_duration,
        Chapter.name.label('chapter_name'), Subject.name.label('subject_name')
    ).all()
    
    return render_template("admin/manage_quizzes.html", quizzes=quizzes, form=form)

@app.route("/admin/edit_quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_quiz(quiz_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    form.chapter_id.choices = [(c.id, f"{c.name} ({Subject.query.get(c.subject_id).name})") 
                              for c in Chapter.query.all()]
    
    if form.validate_on_submit():
        quiz.name = form.name.data
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.time_duration = form.time_duration.data
        quiz.chapter_id = form.chapter_id.data
        db.session.commit()
        flash('Quiz updated successfully', 'success')
        return redirect(url_for('admin_manage_quizzes'))
    
    return render_template('admin/edit_quiz.html', form=form, quiz=quiz)

@app.route("/admin/delete_quiz/<int:quiz_id>", methods=['POST'])
@login_required
def admin_delete_quiz(quiz_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully', 'success')
    return redirect(url_for('admin_manage_quizzes'))

@app.route("/admin/manage_questions", methods=['GET', 'POST'])
@login_required
def admin_manage_questions():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    form = QuestionForm()
    
    quizzes = Quiz.query.all()
    chapters = {ch.id: ch.name for ch in Chapter.query.all()}  
    
    form.quiz_id.choices = [(q.id, f"{q.name} ({chapters.get(q.chapter_id, 'Unknown Chapter')})") 
                            for q in quizzes]
    
    if form.validate_on_submit():
        question = Question(
            question_statement=form.question_statement.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_option=form.correct_option.data,
            quiz_id=form.quiz_id.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question created successfully', 'success')
        return redirect(url_for('admin_manage_questions'))
    
    quiz_filter = request.args.get('quiz_id', None, type=int)
    if quiz_filter:
        questions = Question.query.filter_by(quiz_id=quiz_filter).all()
        current_quiz = Quiz.query.get(quiz_filter)
    else:
        questions = Question.query.all()
        current_quiz = None

    quiz_lookup = {q.id: q.name for q in quizzes}

    return render_template("admin/manage_questions.html", 
                           questions=questions, 
                           form=form, 
                           quizzes=quizzes, 
                           current_quiz=current_quiz, 
                           quiz_lookup=quiz_lookup)  


@app.route("/admin/edit_question/<int:question_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_question(question_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    form.quiz_id.choices = [(q.id, f"{q.name} ({Chapter.query.get(q.chapter_id).name})") 
                          for q in Quiz.query.all()]
    
    if form.validate_on_submit():
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data
        question.quiz_id = form.quiz_id.data
        db.session.commit()
        flash('Question updated successfully', 'success')
        return redirect(url_for('admin_manage_questions'))
    
    return render_template('admin/edit_question.html', form=form, question=question)

@app.route("/admin/delete_question/<int:question_id>", methods=['POST'])
@login_required
def admin_delete_question(question_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully', 'success')
    return redirect(url_for('admin_manage_questions'))


@app.route("/admin/manage_users")
@login_required
def admin_manage_users():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    users = User.query.filter(User.username != "admin@quizmaster.com").all()
    return render_template("admin/manage_users.html", users=users, csrf_token=generate_csrf)

@app.route("/admin/delete_user/<int:user_id>", methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    if user.username == "admin@quizmaster.com":
        flash('Cannot delete admin user', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    
    return redirect(url_for('admin_manage_users'))


@app.route("/take_quiz/<int:quiz_id>")
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('This quiz has no questions yet', 'warning')
        return redirect(url_for('dashboard'))
    

    forms = []
    for question in questions:
        form = QuestionAnswerForm()
        form.question_id.data = question.id
        form.selected_option.choices = [
            (1, question.option1),
            (2, question.option2),
            (3, question.option3),
            (4, question.option4)
        ]
        forms.append((question, form))
    
    return render_template('take_quiz.html', quiz=quiz, forms=forms)

@app.route("/submit_quiz/<int:quiz_id>", methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    total_questions = len(questions)
    correct_answers = 0
    
    for question in questions:
        selected_option = request.form.get(f'selected_option-{question.id}')
        if selected_option and int(selected_option) == question.correct_option:
            correct_answers += 1

    # Add total_questions to prevent IntegrityError
    score = Score(
        total_scored=correct_answers,
        total_questions=total_questions,
        quiz_id=quiz_id,
        user_id=current_user.id
    )
    db.session.add(score)
    db.session.commit()
    
    return redirect(url_for('view_score', score_id=score.id))

@app.route("/view_score/<int:score_id>")
@login_required
def view_score(score_id):
    score = Score.query.get_or_404(score_id)
    

    if score.user_id != current_user.id and current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this score", 'danger')
        return redirect(url_for('dashboard'))
    
    quiz = Quiz.query.get(score.quiz_id)
    questions = Question.query.filter_by(quiz_id=score.quiz_id).count()
    percentage = (score.total_scored / questions) * 100 if questions > 0 else 0
    
    return render_template('view_score.html', 
                          score=score, 
                          quiz=quiz, 
                          total_questions=questions, 
                          percentage=percentage)

@app.route("/my_scores")
@login_required
def my_scores():
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).all()
    

    score_data = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        questions_count = Question.query.filter_by(quiz_id=score.quiz_id).count()
        percentage = (score.total_scored / questions_count) * 100 if questions_count > 0 else 0
        
        score_data.append({
            'score': score,
            'quiz': quiz,
            'chapter': chapter,
            'subject': subject,
            'questions_count': questions_count,
            'percentage': percentage
        })
    
    return render_template('my_scores.html', score_data=score_data)


@app.route("/api/subjects", methods=['GET'])
def api_subjects():
    subjects = Subject.query.all()
    subject_list = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    return jsonify({'subjects': subject_list})

@app.route("/api/chapters/<int:subject_id>", methods=['GET'])
def api_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    chapter_list = [{'id': c.id, 'name': c.name, 'description': c.description} for c in chapters]
    return jsonify({'chapters': chapter_list})

@app.route("/api/quizzes/<int:chapter_id>", methods=['GET'])
def api_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    quiz_list = [{
        'id': q.id, 
        'name': q.name, 
        'date_of_quiz': q.date_of_quiz.strftime('%Y-%m-%d'),
        'time_duration': q.time_duration
    } for q in quizzes]
    return jsonify({'quizzes': quiz_list})

@app.route("/api/quiz_stats", methods=['GET'])
@login_required
def api_quiz_stats():

    if current_user.username == "admin@quizmaster.com":
        scores = Score.query.all()
    else:
        scores = Score.query.filter_by(user_id=current_user.id).all()
    
    stats = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if quiz:
            if quiz.name not in stats:
                stats[quiz.name] = {
                    'attempts': 0,
                    'total_scored': 0,
                    'max_score': 0,
                    'questions': Question.query.filter_by(quiz_id=quiz.id).count()
                }
            stats[quiz.name]['attempts'] += 1
            stats[quiz.name]['total_scored'] += score.total_scored
            stats[quiz.name]['max_score'] = max(stats[quiz.name]['max_score'], score.total_scored)
    

    for quiz_name, data in stats.items():
        if data['attempts'] > 0:
            data['average'] = data['total_scored'] / data['attempts']
        else:
            data['average'] = 0
    
    return jsonify({'stats': stats})

@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

@app.route("/admin/search", methods=['GET'])
@login_required
def admin_search():
    if current_user.username != "admin@quizmaster.com":
        flash("You do not have access to this page", 'danger')
        return redirect(url_for("home"))
    
    search_query = request.args.get('search_query', '')
    search_type = request.args.get('search_type', 'user')
    results = []
    
    if search_query:
        # Wildcard search pattern
        search_pattern = f"%{search_query}%"
        
        if search_type == 'user':
            results = User.query.filter(
                (User.username.like(search_pattern) | 
                 User.fullname.like(search_pattern)) &
                (User.username != "admin@quizmaster.com")
            ).all()
        elif search_type == 'subject':
            results = Subject.query.filter(
                Subject.name.like(search_pattern) | 
                Subject.description.like(search_pattern)
            ).all()
        elif search_type == 'chapter':
            results = Chapter.query.join(Subject).with_entities(
                Chapter.id, Chapter.name, Chapter.description, 
                Subject.name.label('subject_name')
            ).filter(
                Chapter.name.like(search_pattern) | 
                Chapter.description.like(search_pattern)
            ).all()
        elif search_type == 'quiz':
            results = Quiz.query.join(Chapter).join(Subject).with_entities(
                Quiz.id, Quiz.name, Quiz.date_of_quiz, Quiz.time_duration,
                Chapter.name.label('chapter_name'), Subject.name.label('subject_name')
            ).filter(
                Quiz.name.like(search_pattern)
            ).all()
        elif search_type == 'question':
            results = Question.query.join(Quiz).with_entities(
                Question.id, Question.question_statement, 
                Quiz.name.label('quiz_name')
            ).filter(
                Question.question_statement.like(search_pattern)
            ).all()
    
    return render_template("admin/search.html", results=results, search_type=search_type, search_query=search_query)

@app.route("/search", methods=['GET'])
@login_required
def user_search():
    search_query = request.args.get('search_query', '')
    search_type = request.args.get('search_type', 'subject')
    results = []
    
    if search_query:
        # Wildcard search pattern
        search_pattern = f"%{search_query}%"
        
        if search_type == 'subject':
            results = Subject.query.filter(
                Subject.name.like(search_pattern) | 
                Subject.description.like(search_pattern)
            ).all()
        elif search_type == 'quiz':
            results = Quiz.query.join(Chapter).join(Subject).with_entities(
                Quiz.id, Quiz.name, Quiz.date_of_quiz, Quiz.time_duration,
                Chapter.name.label('chapter_name'), Subject.name.label('subject_name')
            ).filter(
                Quiz.name.like(search_pattern)
            ).all()
    
    return render_template("search.html", results=results, search_type=search_type, search_query=search_query)



