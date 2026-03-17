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
    new_student = Student(
        id=str(uuid.uuid4()),
        name=data['name'],
        age=int(data['age']),
        section=data['section']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"success": True, "student": {"id": new_student.id, "name": new_student.name, "section": new_student.section, "age": new_student.age}})

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
    return jsonify({"success": True, "student": {"id": student.id, "name": student.name, "section": student.section, "age": student.age}})

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
    student = Student.query.get(data.get('student_id'))
    if not student:
        return jsonify({"error": "Student not found"}), 400
    new_grade = Grade(
        id=str(uuid.uuid4()),
        student_id=data['student_id'],
        subject=data['subject'],
        score=int(data['score'])
    )
    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"success": True, "grade": {"subject": new_grade.subject, "score": new_grade.score, "student_id": new_grade.student_id}})

# --- Create Database ---
with app.app_context():
    db.create_all()

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
:root { --sidebar-width: 280px; }
body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.sidebar { position: fixed; top:0; left:0; width: var(--sidebar-width); height:100vh; background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:2rem; overflow-y:auto; }
.sidebar h2 { margin-bottom:2rem; font-weight:700; font-size:1.5rem; }
.stat-card { background: rgba(255,255,255,0.1); border-radius:12px; padding:1.5rem; margin-bottom:1rem; backdrop-filter:blur(5px); }
.stat-card h5 { font-size:0.9rem; opacity:0.8; margin-bottom:0.5rem; }
.stat-card h3 { font-size:2rem; font-weight:700; margin:0; }
.main-content { margin-left: var(--sidebar-width); padding:2rem; width:calc(100% - var(--sidebar-width)); }
.card { border:none; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-bottom:1.5rem; }
.card-header { background-color:white; border-bottom:1px solid #eee; font-weight:600; padding:1.25rem 1.5rem; border-radius:12px 12px 0 0 !important; }
.table th { border-top:none; font-weight:600; color:#888; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.5px; }
.table td { vertical-align: middle; padding:1rem; }
.btn-action { padding:0.25rem 0.5rem; font-size:0.8rem; margin-right:5px; }
.grade-badge { font-size:0.8rem; margin-right:5px; margin-bottom:5px; display:inline-block; }
.grade-badge.low { background-color:#ffcdd2; color:#c62828; }
.grade-badge.med { background-color:#fff9c4; color:#f9a825; }
.grade-badge.high { background-color:#c8e6c9; color:#2e7d32; }
.chart-container { position:relative; height:300px; width:100%; }
.modal-content { border-radius:12px; }
</style>
</head>
<body>
<nav class="sidebar">
<h2><i class="bi bi-mortarboard-fill me-2"></i>EduBoard</h2>
<div class="stat-card"><h5>Total Students</h5><h3 id="totalStudents">{{ students|length }}</h3></div>
<div class="stat-card"><h5>Total Grades</h5><h3 id="totalGrades">{{ grades|length }}</h3></div>
<div class="stat-card"><h5>Class Average</h5>
<h3 id="classAvg">{% set total_score = grades | sum(attribute='score') %}{% set count = grades | length %}{{ (total_score / count) | round(1) if count>0 else 0 }}%</h3></div>
<div class="mt-4">
<h6 class="text-uppercase text-white-50 mb-3" style="font-size:0.8rem;">Quick Actions</h6>
<button class="btn btn-light w-100 mb-2 text-start" onclick="openAddStudentModal()"><i class="bi bi-person-plus me-2"></i>Add Student</button>
<button class="btn btn-light w-100 text-start" onclick="openAddGradeModal()"><i class="bi bi-journal-plus me-2"></i>Add Grade</button>
</div>
</nav>

<main class="main-content">
<div class="row">
<div class="col-lg-8">
<div class="card">
<div class="card-header d-flex justify-content-between align-items-center">
<span>Student Directory</span>
<span class="badge bg-primary rounded-pill" id="studentCount">{{ students|length }} Students</span>
</div>
<div class="card-body">
<div class="table-responsive">
<table class="table table-hover" id="studentsTable">
<thead><tr><th>Student</th><th>Age</th><th>Section</th><th>Performance</th><th>Avg</th><th>Actions</th></tr></thead>
<tbody>
{% for student in students %}
<tr id="row-{{student.id}}">
<td>{{ student.name }}</td>
<td>{{ student.age }}</td>
<td>{{ student.section }}</td>
<td>
{% for g in student.grades %}
{% set cls = 'low' if g.score<50 else ('med' if g.score<75 else 'high') %}
<span class="badge grade-badge {{ cls }}">{{ g.subject }}: {{ g.score }}</span>
{% endfor %}
{% if not student.grades %}<span class="text-muted small">No grades</span>{% endif %}
</td>
<td>{{ calculate_average(student) }}</td>
<td>
<button class="btn btn-sm btn-outline-primary btn-action" onclick="editStudent('{{student.id}}','{{student.name}}','{{student.age}}','{{student.section}}')"><i class="bi bi-pencil"></i></button>
<button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteStudent('{{student.id}}')"><i class="bi bi-trash"></i></button>
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
</div></div></div>

<div class="col-lg-4">
<div class="card"><div class="card-header">Performance Distribution</div>
<div class="card-body"><div class="chart-container"><canvas id="performanceChart"></canvas></div></div></div>
</div>
</div>
</main>

<!-- Add Student Modal -->
<div class="modal fade" id="addStudentModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content">
<div class="modal-header"><h5 class="modal-title">Add Student</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
<div class="modal-body">
<form id="addStudentForm">
<input type="text" class="form-control mb-2" name="name" placeholder="Name" required>
<input type="number" class="form-control mb-2" name="age" placeholder="Age" required>
<input type="text" class="form-control mb-2" name="section" placeholder="Section" required>
</form>
</div>
<div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
<button type="button" class="btn btn-primary" onclick="submitAddStudent()">Save</button></div></div></div></div>

<!-- Add Grade Modal -->
<div class="modal fade" id="addGradeModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content">
<div class="modal-header"><h5 class="modal-title">Add Grade</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
<div class="modal-body">
<form id="addGradeForm">
<select class="form-select mb-2" name="student_id" required>
{% for s in students %}<option value="{{ s.id }}">{{ s.name }} ({{ s.section }})</option>{% endfor %}
</select>
<input type="text" class="form-control mb-2" name="subject" placeholder="Subject" required>
<input type="number" class="form-control mb-2" name="score" placeholder="Score" min="0" max="100" required>
</form>
</div>
<div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
<button type="button" class="btn btn-primary" onclick="submitAddGrade()">Save Grade</button></div></div></div></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
// --- Modals ---
const addStudentModal = new bootstrap.Modal(document.getElementById('addStudentModal'));
const addGradeModal = new bootstrap.Modal(document.getElementById('addGradeModal'));
function openAddStudentModal(){document.getElementById('addStudentForm').reset(); addStudentModal.show();}
function openAddGradeModal(){document.getElementById('addGradeForm').reset(); addGradeModal.show();}

// --- API Calls ---
function submitAddStudent(){
    const form = document.getElementById('addStudentForm');
    const data = Object.fromEntries(new FormData(form));
    fetch('/api/student/add',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
    .then(r=>r.json()).then(resp=>{
        if(resp.success){location.reload();}
    });
}

function submitAddGrade(){
    const form = document.getElementById('addGradeForm');
    const data = Object.fromEntries(new FormData(form));
    if(!data.student_id || !data.subject || !data.score){alert("Fill all fields"); return;}
    data.score = parseInt(data.score);
    fetch('/api/grade/add',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
    .then(r=>r.json()).then(resp=>{
        if(resp.success){addGradeModal.hide(); location.reload();} else {alert(resp.error);}
    });
}

// Optional: implement edit/delete functions here similar to your previous code
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
