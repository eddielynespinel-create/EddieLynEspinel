from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import uuid

app = Flask(__name__)

# Data storage
students = []
grades = []

# Helper function to get grades for a student
def get_student_grades(student_id):
    return [g for g in grades if g["student_id"] == student_id]

# Home page with interactive UI
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student & Grades Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="text-center text-primary">Student & Grades Management</h1>
            
            <h3 class="mt-4">Add Student</h3>
            <form action="/add_student" method="post" class="row g-3 mb-4">
                <div class="col">
                    <input type="text" class="form-control" name="name" placeholder="Name" required>
                </div>
                <div class="col">
                    <input type="number" class="form-control" name="age" placeholder="Age" required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" name="section" placeholder="Section" required>
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-success mb-3">Add Student</button>
                </div>
            </form>
            
            <h3 class="mt-4">Add Grade</h3>
            <form action="/add_grade" method="post" class="row g-3 mb-4">
                <div class="col">
                    <select class="form-control" name="student_id" required>
                        <option value="">Select Student</option>
                        {% for student in students %}
                        <option value="{{student.id}}">{{student.name}}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col">
                    <input type="text" class="form-control" name="subject" placeholder="Subject" required>
                </div>
                <div class="col">
                    <input type="number" class="form-control" name="score" placeholder="Score" required>
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-primary mb-3">Add Grade</button>
                </div>
            </form>
            
            <h3 class="mt-4">Students & Their Grades</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Section</th>
                        <th>Grades (Subject: Score)</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{student.name}}</td>
                        <td>{{student.age}}</td>
                        <td>{{student.section}}</td>
                        <td>
                            {% for g in get_student_grades(student.id) %}
                                {{g.subject}}: {{g.score}}<br>
                            {% endfor %}
                        </td>
                        <td>
                            <a href="/edit_student/{{student.id}}" class="btn btn-warning btn-sm">Edit</a>
                            <a href="/delete_student/{{student.id}}" class="btn btn-danger btn-sm">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, students=students, get_student_grades=get_student_grades)

# Add student
@app.route('/add_student', methods=['POST'])
def add_student():
    new_student = {
        "id": str(uuid.uuid4()),
        "name": request.form["name"],
        "age": int(request.form["age"]),
        "section": request.form["section"]
    }
    students.append(new_student)
    return redirect(url_for('home'))

# Edit student form
@app.route('/edit_student/<student_id>')
def edit_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return "Student not found", 404
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Student</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1>Edit Student</h1>
            <form action="/update_student/{{student.id}}" method="post" class="row g-3">
                <div class="col">
                    <input type="text" class="form-control" name="name" value="{{student.name}}" required>
                </div>
                <div class="col">
                    <input type="number" class="form-control" name="age" value="{{student.age}}" required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" name="section" value="{{student.section}}" required>
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-success">Update</button>
                    <a href="/" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, student=student)

# Update student
@app.route('/update_student/<student_id>', methods=['POST'])
def update_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return "Student not found", 404
    student["name"] = request.form["name"]
    student["age"] = int(request.form["age"])
    student["section"] = request.form["section"]
    return redirect(url_for('home'))

# Delete student
@app.route('/delete_student/<student_id>')
def delete_student(student_id):
    global students, grades
    students = [s for s in students if s["id"] != student_id]
    grades = [g for g in grades if g["student_id"] != student_id]  # remove grades for this student
    return redirect(url_for('home'))

# Add grade
@app.route('/add_grade', methods=['POST'])
def add_grade():
    new_grade = {
        "id": str(uuid.uuid4()),
        "student_id": request.form["student_id"],
        "subject": request.form["subject"],
        "score": int(request.form["score"])
    }
    grades.append(new_grade)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
