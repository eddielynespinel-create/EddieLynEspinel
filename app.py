from flask import Flask, jsonify, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import uuid

# --- Flask App & Database ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'  # Local SQLite DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class Student(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String, nullable=False)
    grades = db.relationship('Grade', backref='student', cascade="all, delete-orphan")

class Grade(db.Model):
    id = db.Column(db.String, primary_key=True)
    student_id = db.Column(db.String, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)

# --- Helper Functions ---
def calculate_average(student):
    if not student.grades:
        return 0
    return round(sum(g.score for g in student.grades) / len(student.grades), 2)

# --- Routes ---
@app.route('/')
def home():
    students = Student.query.all()
    grades = Grade.query.all()
    return render_template_string(HTML_TEMPLATE, students=students, grades=grades, calculate_average=calculate_average)

# --- API Routes ---
@app.route('/api/student/add', methods=['POST'])
def api_add_student():
    data = request.json
    new_student = Student(id=str(uuid.uuid4()), name=data['name'], age=int(data['age']), section=data['section'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"success": True, "student": {"id": new_student.id, "name": new_student.name}})

@app.route('/api/student/edit/<student_id>', methods=['POST'])
def api_edit_student(student_id):
    student = Student.query.get(student_id)
    data = request.json
    if not student:
        return jsonify({"error": "Student not found"}), 404
    student.name = data.get('name', student.name)
    student.age = int(data.get('age', student.age))
    student.section = data.get('section', student.section)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/student/delete/<student_id>', methods=['DELETE'])
def api_delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
    return jsonify({"success": True})

@app.route('/api/grade/add', methods=['POST'])
def api_add_grade():
    data = request.json
    new_grade = Grade(
        id=str(uuid.uuid4()),
        student_id=data['student_id'],
        subject=data['subject'],
        score=int(data['score'])
    )
    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"success": True})

# --- HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Student Management Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
/* Your previous full CSS goes here */
</style>
</head>
<body>
<!-- Your previous full HTML content goes here, replace any Jinja references with the ones compatible with SQLAlchemy -->
<!-- Example: {{ students|length }} => {{ students|length }} works, and {{ calculate_average(student) }} works -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
// Your previous JS for modals and API calls goes here
</script>
</body>
</html>
"""

# --- Create Database ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
