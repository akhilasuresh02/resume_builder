import os
import urllib.parse
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use env for secret key

# Database configuration
dbname = os.getenv('DB_NAME', 'resume_db')
user = os.getenv('DB_USER', 'myuser')
password = os.getenv('DB_PASSWORD', 'mypassword')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')

# URL-encode username and password to handle special characters
encoded_user = urllib.parse.quote(user)
encoded_password = urllib.parse.quote(password)

# Construct SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{host}:{port}/{dbname}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Debug: Print the URI to verify
print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise

class User(db.Model):
    __tablename__ = 'user'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()


@app.route('/logout')
def logout():
    # Clear the user session
    session.pop('user_id', None)  # Remove user_id from session, if it exists
    session.pop('username', None)  # Remove username from session, if it exists
    return redirect(url_for('home'))  # Redirect to the 'home' endpoint without flash

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Welcome, " + username, "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")  # Keep login success message
            return redirect(url_for("dashboard"))
        else:
            flash("Login unsuccessful! Invalid credentials.", "danger")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your dashboard.", "danger")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("dashboard.html", resumes=resumes)

@app.route('/add_resume', methods=['GET', 'POST'])
def add_resume():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add a resume.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        summary = request.form["summary"]
        email = request.form["email"]
        phone = request.form["phone"]
        action = request.form.get("action")  # Check if "Next" was clicked

        cur.execute("""
            INSERT INTO resumes (user_id, title, summary, email, phone)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (user_id, title, summary, email, phone))
        resume_id = cur.fetchone()[0]
        conn.commit()

        # Store the latest resume_id in session
        session['latest_resume_id'] = resume_id
        flash("Resume added successfully!", "success")

        if action == "next":
            cur.close()
            conn.close()
            return redirect(url_for("add_work_experience"))
        else:
            cur.close()
            conn.close()
            return redirect(url_for("dashboard"))

    cur.close()
    conn.close()
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
        description = request.form.get("description") or None
        action = request.form.get("action")  # Check if "Next" was clicked

        cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
        if not cur.fetchone():
            flash("Invalid resume selected.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("add_work_experience"))

        cur.execute("""
            INSERT INTO work_experience (resume_id, job_title, company_name, location, start_date, end_date, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (resume_id, job_title, company_name, location, start_date, end_date, description))
        conn.commit()
        flash("Work experience added successfully!", "success")

        if action == "next":
            cur.close()
            conn.close()
            return redirect(url_for("add_education"))
        else:
            cur.close()
            conn.close()
            return redirect(url_for("add_education"))  # Ensures message displays on /education

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
    print(f"User ID: {user_id}")

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        resume_id = request.form["resume_id"]
        levels = ['10th', '12th', 'Under Graduate', 'Post Graduate']

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
            programme = request.form.get(f"{level}_programme") or None

            if institution and start_year and aggregate:  # Only insert if required fields are present
                cur.execute("""
                    INSERT INTO education (resume_id, level, institution, start_year, end_year, is_pursuing, aggregate, programme)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (resume_id, level, institution, start_year, end_year, is_pursuing, aggregate, programme))

        conn.commit()
        flash("Education added successfully!", "success")
        cur.close()
        conn.close()

        action = request.form.get("action")
        if action == "next":
            return redirect(url_for("add_skills"))
        else:
            return redirect(url_for("dashboard"))

    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    print(f"Resumes fetched: {resumes}")
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
        resume_id = request.form.get("resume_id")
        skill_name = request.form.get("skill_name")

        if resume_id:
            cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
            if not cur.fetchone():
                flash("Invalid resume selected.", "danger")
                cur.close()
                conn.close()
                return redirect(url_for("add_skills"))

            if skill_name:
                cur.execute("""
                    INSERT INTO skills (resume_id, skill_name)
                    VALUES (%s, %s)
                """, (resume_id, skill_name))
                conn.commit()
                flash("Skill added successfully!", "success")

        cur.close()
        conn.close()

        action = request.form.get("action")
        if action == "next":
            return redirect(url_for("add_achievements"))
        else:
            return redirect(url_for("dashboard"))

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

        action = request.form.get("action")
        if action == "next":
            return redirect(url_for("add_languages"))
        else:
            return redirect(url_for("add_achievements"))

    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    latest_resume_id = session.get('latest_resume_id')
    cur.close()
    conn.close()
    return render_template("achievements.html", resumes=resumes, latest_resume_id=latest_resume_id)

@app.route('/add_languages', methods=['GET', 'POST'])
def add_languages():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add languages.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        resume_id = request.form["resume_id"]
        language_name = request.form["language_name"]
        proficiency_level = request.form["proficiency_level"]

        cur.execute("SELECT id FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
        if not cur.fetchone():
            flash("Invalid resume selected.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("add_languages"))

        cur.execute("""
            INSERT INTO languages (resume_id, language_name, proficiency_level)
            VALUES (%s, %s, %s)
        """, (resume_id, language_name, proficiency_level))
        conn.commit()
        flash("Language added successfully!", "success")
        cur.close()
        conn.close()

        action = request.form.get("action")
        if action == "dashboard":
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("add_languages"))

    cur.execute("SELECT id, title FROM resumes WHERE user_id = %s", (user_id,))
    resumes = cur.fetchall()
    latest_resume_id = session.get('latest_resume_id')
    cur.close()
    conn.close()
    return render_template("add_languages.html", resumes=resumes, latest_resume_id=latest_resume_id)

@app.route('/generate-resume/<int:resume_id>')
def generate_resume(resume_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your resume.", "danger")
        return redirect(url_for("login"))
    
    print(f"Generating resume for resume_id: {resume_id}")  # Debug resume_id
    
    conn = get_db_connection()
    print("Connection established")  # Debug connection
    cur = conn.cursor()
    
    # Fetch the specific resume for the user
    cur.execute("SELECT * FROM resumes WHERE id = %s AND user_id = %s", (resume_id, user_id))
    resume = cur.fetchone()
    
    if not resume:
        cur.close()
        conn.close()
        flash("Resume not found or you don't have access.", "danger")
        return redirect(url_for("dashboard"))
    
    # Fetch related data
    cur.execute("SELECT * FROM work_experience WHERE resume_id = %s", (resume_id,))
    work_experience = cur.fetchall()
    
    cur.execute("SELECT * FROM education WHERE resume_id = %s", (resume_id,))
    education = cur.fetchall()
    
    cur.execute("SELECT * FROM skills WHERE resume_id = %s", (resume_id,))
    skills = cur.fetchall()
    
    cur.execute("SELECT * FROM achievements WHERE resume_id = %s", (resume_id,))
    achievements = cur.fetchall()
    
    cur.execute("SELECT * FROM languages WHERE resume_id = %s", (resume_id,))
    languages = cur.fetchall()
    print(f"Languages fetched: {languages}")  # Debug languages data
    
    cur.close()
    conn.close()
    
    return render_template(
        "generated_resume.html",
        resume=resume,
        work_experience=work_experience,
        education=education,
        skills=skills,
        achievements=achievements,
        languages=languages
    )

@app.route('/generate-resume')
def generate_resume_legacy():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your resume.", "danger")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch the latest resume for the user
    cur.execute("SELECT id FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    resume = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if resume:
        return redirect(url_for('generate_resume', resume_id=resume[0]))
    else:
        flash("No resume found. Please add one first.", "danger")
        return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
