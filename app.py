from flask import Flask, jsonify, request, render_template_string
import uuid  # For unique student IDs

app = Flask(__name__)

# Sample student data
students = [
    {"id": str(uuid.uuid4()), "name": "John Doe", "grade": 10, "section": "Zechariah"},
    {"id": str(uuid.uuid4()), "name": "Jane Smith", "grade": 9, "section": "Zechariah"}
]

# Home route with simple UI using Bootstrap
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask API Home</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="text-center text-primary">Welcome to My Flask API</h1>
            <p class="text-center">Use the following endpoints:</p>
            <ul class="list-group mx-auto" style="max-width:400px;">
                <li class="list-group-item"><a href="/student">/student → View students</a></li>
                <li class="list-group-item"><a href="/grade">/grade → Sample grade info</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# Get all students
@app.route('/student', methods=['GET'])
def get_student():
    return jsonify(students)

# Add a new student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "grade": data.get("grade"),
        "section": data.get("section")
    }
    students.append(new_student)
    return jsonify({"message": "Student added successfully!", "student": new_student}), 201

# Update a student
@app.route('/student/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    for student in students:
        if student["id"] == student_id:
            student["name"] = data.get("name", student["name"])
            student["grade"] = data.get("grade", student["grade"])
            student["section"] = data.get("section", student["section"])
            return jsonify({"message": "Student updated!", "student": student})
    return jsonify({"error": "Student not found"}), 404

# Delete a student
@app.route('/student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    for student in students:
        if student["id"] == student_id:
            students.remove(student)
            return jsonify({"message": "Student deleted!"})
    return jsonify({"error": "Student not found"}), 404

# Sample grade endpoint
@app.route('/grade')
def grade():
    return jsonify({"subject": "Math", "grade": 95})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
