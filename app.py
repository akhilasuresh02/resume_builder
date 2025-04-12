import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key

# PostgreSQL Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://myuser:mypassword@localhost/resume_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="resume_db",
        user="myuser",       # Use your actual PostgreSQL username
        password="mypassword" # Use your actual password
    )

# User Model
class User(db.Model):
    __tablename__ = 'user'  # Ensure it maps to the correct table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

# Create Database Tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Create User
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Welcome, " + username, "success")

        # Redirect to login page after registration
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Find user in database
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials, try again!", "danger")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/add_resume", methods=["GET", "POST"])
def add_resume():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add a resume.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        summary = request.form["summary"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO resumes (user_id, title, summary) VALUES (%s, %s, %s) RETURNING id, title",
                    (user_id, title, summary))
        new_resume = cur.fetchone()
        new_resume_id, new_resume_title = new_resume[0], new_resume[1]
        conn.commit()
        cur.close()
        conn.close()

        flash("Resume added successfully!", "success")
        # Store the latest resume ID and title in session
        session['latest_resume_id'] = new_resume_id
        session['latest_resume_title'] = new_resume_title
        # Redirect to education page to use the new resume
        return redirect(url_for("add_education"))

    return render_template("add_resume.html")

@app.route('/work-experience', methods=['GET', 'POST'])
def add_work_experience():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add work experience.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        resume_id = request.form["resume_id"]
        job_title = request.form["job_title"]
        company_name = request.form["company_name"]
        location = request.form["location"]
        start_date = request.form["start_date"]
        end_date = request.form.get("end_date") or None

        # Verify resume belongs to the user
        cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
        if not cur.fetchone():
            flash("Invalid resume selected.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("add_work_experience"))

        cur.execute("""
            INSERT INTO work_experience (resume_id, job_title, company_name, location, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (resume_id, job_title, company_name, location, start_date, end_date))
        conn.commit()
        flash("Work experience added successfully!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("dashboard"))

    # Fetch resumes for the dropdown
    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    latest_resume_id = session.get('latest_resume_id')
    cur.close()
    conn.close()
    return render_template("work_experience.html", resumes=resumes, latest_resume_id=latest_resume_id)

@app.route('/education', methods=['GET', 'POST'])
def add_education():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add education.", "danger")
        return redirect(url_for("login"))
    print(f"User ID: {user_id}")  # Debug print

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        resume_id = request.form["resume_id"]
        levels = ['10th', '12th', 'UG', 'PG']

        # Verify resume belongs to the user
        cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
        if not cur.fetchone():
            flash("Invalid resume selected.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("add_education"))

        for level in levels:
            institution = request.form.get(f"{level}_institution")
            start_year = request.form.get(f"{level}_start_year")
            end_year = request.form.get(f"{level}_end_year") or None
            is_pursuing = True if request.form.get(f"{level}_is_pursuing") else False
            aggregate = request.form.get(f"{level}_aggregate")

            # Insert only if institution and start_year and aggregate are provided
            if institution and start_year and aggregate:
                cur.execute("""
                    INSERT INTO education (resume_id, level, institution, start_year, end_year, is_pursuing, aggregate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (resume_id, level, institution, start_year, end_year, is_pursuing, aggregate))

        conn.commit()
        flash("Education added successfully!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("dashboard"))

    # Fetch resumes for the dropdown
    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    print(f"Resumes fetched: {resumes}")  # Debug print
    latest_resume_id = session.get('latest_resume_id')
    latest_resume_title = session.get('latest_resume_title')
    cur.close()
    conn.close()
    return render_template("education.html", resumes=resumes, latest_resume_id=latest_resume_id, latest_resume_title=latest_resume_title)

@app.route('/skills', methods=['GET', 'POST'])
def add_skills():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add skills.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        resume_id = request.form["resume_id"]
        skill_name = request.form["skill_name"]

        # Verify resume belongs to the user
        cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
        if not cur.fetchone():
            flash("Invalid resume selected.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("add_skills"))

        cur.execute("""
            INSERT INTO skills (resume_id, skill_name)
            VALUES (%s, %s)
        """, (resume_id, skill_name))
        conn.commit()
        flash("Skill added successfully!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("add_skills"))

    # Fetch resumes for the dropdown
    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    latest_resume_id = session.get('latest_resume_id')
    cur.close()
    conn.close()
    return render_template("skills.html", resumes=resumes, latest_resume_id=latest_resume_id)

@app.route('/achievements', methods=['GET', 'POST'])
def add_achievements():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add achievements.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        resume_id = request.form["resume_id"]
        type = request.form["type"]
        name = request.form["name"]
        description = request.form["description"]

        # Verify resume belongs to the user
        cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
        if not cur.fetchone():
            flash("Invalid resume selected.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("add_achievements"))

        cur.execute("""
            INSERT INTO achievements (resume_id, type, name, description)
            VALUES (%s, %s, %s, %s)
        """, (resume_id, type, name, description))
        conn.commit()
        flash("Achievement added successfully!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("add_achievements"))

    # Fetch resumes for the dropdown
    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    latest_resume_id = session.get('latest_resume_id')
    cur.close()
    conn.close()
    return render_template("achievements.html", resumes=resumes, latest_resume_id=latest_resume_id)

@app.route('/generate-resume')
def generate_resume():
    user_id = session.get('user_id')  # Use session-based logic

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch latest resume for the user
    cur.execute("SELECT * FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    resume = cur.fetchone()

    if resume:
        resume_id = resume[0]

        cur.execute("SELECT * FROM work_experience WHERE resume_id = %s", (resume_id,))
        work_experience = cur.fetchall()

        cur.execute("SELECT * FROM education WHERE resume_id = %s", (resume_id,))
        education = cur.fetchall()

        cur.execute("SELECT * FROM skills WHERE resume_id = %s", (resume_id,))
        skills = cur.fetchall()

        cur.execute("SELECT * FROM achievements WHERE resume_id = %s", (resume_id,))
        achievements = cur.fetchall()

        cur.close()
        conn.close()
        return render_template("resume_preview.html", resume=resume, work_experience=work_experience, education=education, skills=skills, achievements=achievements)

    cur.close()
    conn.close()
    return "No resume found. Please add one first.", 404

if __name__ == "__main__":
    app.run(debug=True)