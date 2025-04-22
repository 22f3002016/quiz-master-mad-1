# Quiz Master - Project
---

## Description
Quiz Master is a multi-user application designed to facilitate quiz-based learning and assessment. It supports two types of users: **Admins** and **Students**. Admins are responsible for managing quiz content, while Students can attempt quizzes and track their progress through a personalized dashboard.

### Key Features:
- User Authentication and Management
- Quiz Creation and Management
- Real-time Score Tracking
- Performance Visualization through Summary Charts
- Intuitive UI and API-based interaction

---

## Frameworks and Libraries Used

### Backend:
- **Flask** - API Management
- **Flask-Login** - User Authentication
- **Flask-SQLAlchemy** - ORM for Database Management
- **SQLite** - Database

### Frontend:
- **HTML, CSS, Bootstrap** - UI Design
- **Jinja2** - Template Rendering
- **Chart.js** - Data Visualization

---

## Database Schema

- **User Table:**
  - `id` (Primary Key)
  - `username`
  - `password_hash`
  - `fullname`
  - `qualification`
  - `dob`
- **Subject Table:**
  - `id` (Primary Key)
  - `subject_name`
  - `description`
- **Chapter Table:**
  - `id` (Primary Key)
  - `subject_id` (Foreign Key)
  - `chapter_name`
- **Quiz Table:**
  - `id` (Primary Key)
  - `name`
  - `date_of_quiz`
  - `time_duration`
  - `chapter_id` (Foreign Key)
- **Question Table:**
  - `id` (Primary Key)
  - `question_statement`
  - `options`
  - `correct_option`
  - `quiz_id` (Foreign Key)
- **Score Table:**
  - `id` (Primary Key)
  - `user_id` (Foreign Key)
  - `quiz_id` (Foreign Key)
  - `total_scored`
  - `timestamp`

---

## Approach Used

### Role-Based Access Control (RBAC):
- **Admins**: Create, edit, and delete quizzes, questions, and subjects.
- **Students**: Attempt quizzes and view results.

### Authentication:
- Secure login and password management using **Flask-Login**.
- Passwords are hashed using **Werkzeug** for security.

### Data Management:
- **SQLite** is used for data storage, ensuring lightweight and efficient management.

---

## Features and Functionalities

### User Authentication
- Login and registration for Students.
- Admins are pre-registered.

### Quiz Management
- Admins can create, edit, and delete quizzes, questions, and subjects.

### Quiz Attempting
- Students can attempt quizzes within a specified time limit.

### Score Tracking
- Real-time updates of quiz scores and progress tracking.

### Dashboard
- Personalized dashboard for Students using **Chart.js** for visualizations.

### Admin Analytics
- Admins can view performance reports, including quiz statistics and user progress.

---

## Application Architecture

- **Backend:** Python Flask using SQLAlchemy ORM for database interactions and RESTful API development.
- **Frontend:** HTML, CSS, Bootstrap, and Jinja2 for dynamic content rendering.
- **Database:** SQLite for storing user data, quizzes, questions, and scores.

---

## Presentation Video
Watch the project presentation here: **[MAD-1-22f3002016-QuizMaster.mp4](https://www.youtube.com/watch?v=BNz9401mPs4)**
