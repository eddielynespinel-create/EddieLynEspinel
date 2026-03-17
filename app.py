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
:root { --sidebar-width: 280px; }
body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; z-index: 1000; overflow-y: auto; }
.sidebar h2 { font-weight: 700; margin-bottom: 2rem; font-size: 1.5rem; }
.sidebar .stat-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; backdrop-filter: blur(5px); }
.sidebar .stat-card h5 { font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem; }
.sidebar .stat-card h3 { font-size: 2rem; font-weight: 700; margin: 0; }
.main-content { margin-left: var(--sidebar-width); padding: 2rem; width: calc(100% - var(--sidebar-width)); }
.card { border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 1.5rem; }
.card-header { background-color: white; border-bottom: 1px solid #eee; font-weight: 600; padding: 1.25rem 1.5rem; border-radius: 12px 12px 0 0 !important; }
.table th { border-top: none; font-weight: 600; color: #888; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
.table td { vertical-align: middle; padding: 1rem; }
.btn-action { padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-right: 5px; }
.grade-badge { font-size: 0.8rem; margin-right: 5px; margin-bottom: 5px; display: inline-block; }
.grade-badge.low { background-color: #ffcdd2; color: #c62828; }
.grade-badge.med { background-color: #fff9c4; color: #f9a825; }
.grade-badge.high { background-color: #c8e6c9; color: #2e7d32; }
.chart-container { position: relative; height: 300px; width: 100%; }
.modal-content { border-radius: 12px; }
</style>
</head>
<body>

<!-- Sidebar -->
<nav class="sidebar">
<h2><i class="bi bi-mortarboard-fill me-2"></i>EduBoard</h2>
<div class="stat-card"><h5>Total Students</h5><h3>{{ students|length }}</h3></div>
<div class="stat-card"><h5>Total Grades</h5><h3>{{ grades|length }}</h3></div>
<div class="stat-card"><h5>Class Average</h5>
<h3>{% set total_score = grades | sum(attribute='score') %}{% set count = grades | length %}{{ (total_score / count) | round(1) if count > 0 else 0 }}%</h3></div>
<div class="mt-4">
<h6 class="text-uppercase text-white-50 mb-3" style="font-size: 0.8rem;">Quick Actions</h6>
<button class="btn btn-light w-100 mb-2 text-start" onclick="openAddStudentModal()"><i class="bi bi-person-plus me-2"></i> Add Student</button>
<button class="btn btn-light w-100 text-start" onclick="openAddGradeModal()"><i class="bi bi-journal-plus me-2"></i> Add Grade</button>
</div>
</nav>

<!-- Main Content -->
<main class="main-content">
<div class="d-flex justify-content-between align-items-center mb-4">
<div><h2 class="mb-1">Student Management</h2><p class="text-muted">Manage your classroom data efficiently</p></div>
</div>

<div class="row">
<!-- Students Table -->
<div class="col-lg-8">
<div class="card">
<div class="card-header d-flex justify-content-between align-items-center">
<span>Student Directory</span>
<span class="badge bg-primary rounded-pill">{{ students|length }} Students</span>
</div>
<div class="card-body">
<div class="table-responsive">
<table class="table table-hover">
<thead>
<tr>
<th>Student</th><th>Age</th><th>Section</th><th>Performance</th><th>Avg</th><th>Actions</th>
</tr>
</thead>
<tbody>
{% for student in students %}
<tr id="row-{{student.id}}">
<td><div class="d-flex align-items-center">
<div class="bg-secondary text-white rounded-circle d-flex justify-content-center align-items-center me-2" style="width: 40px; height: 40px;">{{ student.name[0] }}</div>
<strong>{{ student.name }}</strong></div></td>
<td>{{ student.age }}</td>
<td><span class="badge bg-light text-dark">{{ student.section }}</span></td>
<td>
{% for g in student.grades %}
{% set cls = 'low' if g.score < 50 else ('med' if g.score < 75 else 'high') %}
<span class="badge grade-badge {{ cls }}">{{ g.subject }}: {{ g.score }}</span>
{% endfor %}
{% if not student.grades %}
<span class="text-muted small">No grades</span>
{% endif %}
</td>
<td><strong>{{ calculate_average(student) }}</strong></td>
<td>
<button class="btn btn-sm btn-outline-primary btn-action" onclick="editStudent('{{ student.id }}', '{{ student.name }}', '{{ student.age }}', '{{ student.section }}')"><i class="bi bi-pencil"></i></button>
<button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteStudent('{{ student.id }}')"><i class="bi bi-trash"></i></button>
</td>
</tr>
{% else %}
<tr><td colspan="6" class="text-center text-muted py-5">No students found. Click "Add Student" to begin.</td></tr>
{% endfor %}
</tbody>
</table>
</div>
</div>
</div>
</div>

<!-- Charts / Analytics -->
<div class="col-lg-4">
<div class="card"><div class="card-header">Performance Distribution</div>
<div class="card-body"><div class="chart-container"><canvas id="performanceChart"></canvas></div></div></div>
<div class="card"><div class="card-header">Recent Grades</div>
<div class="card-body p-0">
<ul class="list-group list-group-flush" style="max-height: 300px; overflow-y: auto;">
{% for g in grades[-5:] %}
<li class="list-group-item d-flex justify-content-between align-items-center">
<div><strong>{{ g.subject }}</strong><br>
<small class="text-muted">{% set s_name = (students | selectattr('id', 'eq', g.student_id) | first).name %}{{ s_name if s_name else 'Unknown' }}</small></div>
<span class="badge bg-primary rounded-pill">{{ g.score }}</span>
</li>
{% else %}
<li class="list-group-item text-center text-muted">No grades yet</li>
{% endfor %}
</ul>
</div>
</div>
</div>
</div>
</main>

<!-- Modals -->
<!-- Add Student Modal -->
<div class="modal fade" id="addStudentModal" tabindex="-1">
<div class="modal-dialog">
<div class="modal-content">
<div class="modal-header">
<h5 class="modal-title">Add New Student</h5>
<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
</div>
<div class="modal-body">
<form id="addStudentForm">
<div class="mb-3"><label class="form-label">Name</label><input type="text" class="form-control" name="name" required></div>
<div class="mb-3"><label class="form-label">Age</label><input type="number" class="form-control" name="age" required></div>
<div class="mb-3"><label class="form-label">Section</label><input type="text" class="form-control" name="section" required></div>
</form>
</div>
<div class="modal-footer">
<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
<button type="button" class="btn btn-primary" onclick="submitAddStudent()">Save Student</button>
</div>
</div>
</div>
</div>

<!-- Edit Student Modal -->
<div class="modal fade" id="editStudentModal" tabindex="-1">
<div class="modal-dialog">
<div class="modal-content">
<div class="modal-header">
<h5 class="modal-title">Edit Student</h5>
<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
</div>
<div class="modal-body">
<form id="editStudentForm">
<input type="hidden" name="id" id="edit-student-id">
<div class="mb-3"><label class="form-label">Name</label><input type="text" class="form-control" name="name" id="edit-student-name" required></div>
<div class="mb-3"><label class="form-label">Age</label><input type="number" class="form-control" name="age" id="edit-student-age" required></div>
<div class="mb-3"><label class="form-label">Section</label><input type="text" class="form-control" name="section" id="edit-student-section" required></div>
</form>
</div>
<div class="modal-footer">
<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
<button type="button" class="btn btn-primary" onclick="submitEditStudent()">Update</button>
</div>
</div>
</div>
</div>

<!-- Add Grade Modal -->
<div class="modal fade" id="addGradeModal" tabindex="-1">
<div class="modal-dialog">
<div class="modal-content">
<div class="modal-header">
<h5 class="modal-title">Add Grade</h5>
<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
</div>
<div class="modal-body">
<form id="addGradeForm">
<div class="mb-3"><label class="form-label">Student</label>
<select class="form-select" name="student_id" required>
{% for student in students %}
<option value="{{ student.id }}">{{ student.name }} ({{ student.section }})</option>
{% endfor %}
</select>
</div>
<div class="mb-3"><label class="form-label">Subject</label><input type="text" class="form-control" name="subject" placeholder="e.g., Mathematics" required></div>
<div class="mb-3"><label class="form-label">Score (0-100)</label><input type="number" class="form-control" name="score" min="0" max="100" required></div>
</form>
</div>
<div class="modal-footer">
<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
<button type="button" class="btn btn-primary" onclick="submitAddGrade()">Save Grade</button>
</div>
</div>
</div>
</div>

<!-- JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const addStudentModal = new bootstrap.Modal(document.getElementById('addStudentModal'));
const editStudentModal = new bootstrap.Modal(document.getElementById('editStudentModal'));
const addGradeModal = new bootstrap.Modal(document.getElementById('addGradeModal'));

function openAddStudentModal(){document.getElementById('addStudentForm').reset(); addStudentModal.show();}
function openAddGradeModal(){document.getElementById('addGradeForm').reset(); addGradeModal.show();}
function editStudent(id,name,age,section){document.getElementById('edit-student-id').value=id; document.getElementById('edit-student-name').value=name; document.getElementById('edit-student-age').value=age; document.getElementById('edit-student-section').value=section; editStudentModal.show();}

function submitAddStudent(){
const form= document.getElementById('addStudentForm');
const data= Object.fromEntries(new FormData(form));
fetch('/api/student/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
.then(res=>res.json()).then(resp=>{if(resp.success) location.reload();});
}

function submitEditStudent(){
const form= document.getElementById('editStudentForm');
const id=form.id.value;
const data= Object.fromEntries(new FormData(form));
fetch(`/api/student/edit/${id}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
.then(res=>res.json()).then(resp=>{if(resp.success) location.reload();});
}

function deleteStudent(id){
if(confirm('Are you sure you want to delete this student and all their grades?')){
fetch(`/api/student/delete/${id}`,{method:'DELETE'}).then(res=>res.json()).then(resp=>{if(resp.success) location.reload();});}
}

function submitAddGrade(){
const form= document.getElementById('addGradeForm');
const data= Object.fromEntries(new FormData(form));
fetch('/api/grade/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
.then(res=>res.json()).then(resp=>{if(resp.success) location.reload();});
}

// Chart
const ctx=document.getElementById('performanceChart');
const gradeScores={{ grades | map(attribute='score') | list | tojson }};
const subjects={{ grades | map(attribute='subject') | list | tojson }};
new Chart(ctx,{type:'line',data:{labels:subjects.slice(-10),datasets:[{label:'Score',data:gradeScores.slice(-10),borderColor:'#764ba2',backgroundColor:'rgba(118,75,162,0.2)',tension:0.4,fill:true}]} ,options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,max:100}}}});
</script>

</body>
</html>
"""

# --- Create Database ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
