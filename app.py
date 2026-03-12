from flask import Flask, jsonify, request, render_template_string
import uuid

app = Flask(__name__)

# Sample data
students = [
    {"id": str(uuid.uuid4()), "name": "John Doe", "age": 15, "section": "Zechariah"},
    {"id": str(uuid.uuid4()), "name": "Jane Smith", "age": 14, "section": "Zechariah"}
]

grades = [
    {"id": str(uuid.uuid4()), "student_id": students[0]["id"], "subject": "Math", "score": 95},
    {"id": str(uuid.uuid4()), "student_id": students[1]["id"], "subject": "Science", "score": 88}
]

# Home page with tables
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask Student API</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="text-center text-primary">Welcome to My Flask Student API</h1>
            
            <h3 class="mt-4">Students</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Section</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{student.id}}</td>
                        <td>{{student.name}}</td>
                        <td>{{student.age}}</td>
                        <td>{{student.section}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <h3 class="mt-4">Grades</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Student ID</th>
                        <th>Subject</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for grade in grades %}
                    <tr>
                        <td>{{grade.id}}</td>
                        <td>{{grade.student_id}}</td>
                        <td>{{grade.subject}}</td>
                        <td>{{grade.score}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, students=students, grades=grades)

# API: Get all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# API: Add a student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "age": data.get("age"),
        "section": data.get("section")
    }
    students.append(new_student)
    return jsonify({"message": "Student added", "student": new_student}), 201

# API: Update a student
@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    for student in students:
        if student["id"] == student_id:
            student["name"] = data.get("name", student["name"])
            student["age"] = data.get("age", student["age"])
            student["section"] = data.get("section", student["section"])
            return jsonify({"message": "Student updated", "student": student})
    return jsonify({"error": "Student not found"}), 404

# API: Delete a student
@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    for student in students:
        if student["id"] == student_id:
            students.remove(student)
            return jsonify({"message": "Student deleted"})
    return jsonify({"error": "Student not found"}), 404

# API: Get all grades
@app.route('/grades', methods=['GET'])
def get_grades():
    return jsonify(grades)

# API: Add a grade
@app.route('/grades', methods=['POST'])
def add_grade():
    data = request.get_json()
    new_grade = {
        "id": str(uuid.uuid4()),
        "student_id": data.get("student_id"),
        "subject": data.get("subject"),
        "score": data.get("score")
    }
    grades.append(new_grade)
    return jsonify({"message": "Grade added", "grade": new_grade}), 201

# API: Update a grade
@app.route('/grades/<grade_id>', methods=['PUT'])
def update_grade(grade_id):
    data = request.get_json()
    for grade in grades:
        if grade["id"] == grade_id:
            grade["student_id"] = data.get("student_id", grade["student_id"])
            grade["subject"] = data.get("subject", grade["subject"])
            grade["score"] = data.get("score", grade["score"])
            return jsonify({"message": "Grade updated", "grade": grade})
    return jsonify({"error": "Grade not found"}), 404

# API: Delete a grade
@app.route('/grades/<grade_id>', methods=['DELETE'])
def delete_grade(grade_id):
    for grade in grades:
        if grade["id"] == grade_id:
            grades.remove(grade)
            return jsonify({"message": "Grade deleted"})
    return jsonify({"error": "Grade not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
