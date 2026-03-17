from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class Student(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(50), nullable=False)
    grades = db.relationship('Grade', backref='student', cascade='all, delete-orphan')

class Grade(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# --- Helper Functions ---
def get_student_grades(student_id):
    return Grade.query.filter_by(student_id=student_id).all()

def calculate_average(student_id):
    grades = get_student_grades(student_id)
    if not grades:
        return 0
    return round(sum(g.score for g in grades) / len(grades), 2)

# --- Routes ---
@app.route('/')
def home():
    students = Student.query.all()
    grades = Grade.query.all()
    return render_template('index.html',
                           students=students,
                           grades=grades,
                           get_student_grades=get_student_grades,
                           calculate_average=calculate_average)

# --- API Routes ---

# Add Student
@app.route('/api/student/add', methods=['POST'])
def api_add_student():
    data = request.json
    if not data or not all(k in data for k in ['name', 'age', 'section']):
        return jsonify({"error": "Missing data"}), 400

    new_student = Student(
        id=str(uuid.uuid4()),
        name=data['name'],
        age=int(data['age']),
        section=data['section']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"success": True, "student": {
        "id": new_student.id,
        "name": new_student.name,
        "age": new_student.age,
        "section": new_student.section
    }})

# Edit Student
@app.route('/api/student/edit/<student_id>', methods=['POST'])
def api_edit_student(student_id):
    data = request.json
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    student.name = data.get("name", student.name)
    student.age = int(data.get("age", student.age))
    student.section = data.get("section", student.section)
    db.session.commit()
    return jsonify({"success": True, "student": {
        "id": student.id,
        "name": student.name,
        "age": student.age,
        "section": student.section
    }})

# Delete Student
@app.route('/api/student/delete/<student_id>', methods=['DELETE'])
def api_delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
    return jsonify({"success": True})

# Add Grade
@app.route('/api/grade/add', methods=['POST'])
def api_add_grade():
    data = request.json
    new_grade = Grade(
        id=str(uuid.uuid4()),
        student_id=data["student_id"],
        subject=data["subject"],
        score=int(data["score"])
    )
    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"success": True, "grade": {
        "id": new_grade.id,
        "student_id": new_grade.student_id,
        "subject": new_grade.subject,
        "score": new_grade.score
    }})

# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates SQLite database if not exists
    app.run(debug=True)
