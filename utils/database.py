import os
import json
import uuid
import bcrypt
from datetime import datetime

# Paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ANNOUNCEMENTS_FILE = os.path.join(DATA_DIR, "announcements.json")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.json")
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.json")

def load_json(file_path, default_value=None):
    """
    Safely reads JSON from a file. If file is missing or corrupted, returns default.
    """
    if default_value is None:
        default_value = []
    
    if not os.path.exists(file_path):
        return default_value
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default_value
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return default_value

def save_json(file_path, data):
    """
    Safely writes data to a JSON file.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def init_database():
    """
    Initializes standard database directory and seeding files if missing.
    Always creates a default admin account (username: admin, password: adminpassword).
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Users
    users = load_json(USERS_FILE, [])
    if not users:
        admin_pass_hash = hash_password("adminpassword")
        users = [
            {
                "id": str(uuid.uuid4()),
                "name": "System Administrator",
                "email": "admin@smartcampus.edu",
                "username": "admin",
                "password": admin_pass_hash,
                "role": "Admin"
            }
        ]
        save_json(USERS_FILE, users)
        
    # 2. Announcements
    if not os.path.exists(ANNOUNCEMENTS_FILE):
        save_json(ANNOUNCEMENTS_FILE, [
            {
                "id": str(uuid.uuid4()),
                "title": "Welcome to SmartCampusAI!",
                "content": "This is a campus-wide announcement page. Here you will find regular updates.",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "author_name": "System Administrator",
                "target_role": "All"
            }
        ])
        
    # 3. Attendance
    if not os.path.exists(ATTENDANCE_FILE):
        save_json(ATTENDANCE_FILE, [])
        
    # 4. Assignments
    if not os.path.exists(ASSIGNMENTS_FILE):
        save_json(ASSIGNMENTS_FILE, [])

# User Helper CRUD Operations
def add_user(name, email, username, password_raw, role):
    """
    Inserts a new user into users.json. Passes validation requirements.
    """
    users = load_json(USERS_FILE, [])
    
    # Check duplicate username
    if any(u["username"] == username for u in users):
        return False, "Username already exists."
        
    # Check duplicate email
    if any(u["email"] == email for u in users):
        return False, "Email already exists."
        
    new_user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "username": username,
        "password": hash_password(password_raw),
        "role": role
    }
    
    users.append(new_user)
    if save_json(USERS_FILE, users):
        return True, new_user
    return False, "Failed to write user database."

def update_user(user_id, updated_fields):
    """
    Updates specific elements of user record.
    """
    users = load_json(USERS_FILE, [])
    for u in users:
        if u["id"] == user_id:
            # If resetting password, hash it first
            if "password" in updated_fields and not updated_fields["password"].startswith("$2b$"):
                updated_fields["password"] = hash_password(updated_fields["password"])
            
            # Apply changes
            for key, val in updated_fields.items():
                u[key] = val
                
            save_json(USERS_FILE, users)
            return True, "User updated successfully."
    return False, "User not found."

def delete_user(user_id):
    """
    Deletes user by user ID.
    """
    users = load_json(USERS_FILE, [])
    new_users = [u for u in users if u["id"] != user_id]
    if len(new_users) == len(users):
        return False, "User not found."
    save_json(USERS_FILE, new_users)
    return True, "User deleted successfully."

# Announcements CRUD Operations
def load_announcements():
    return load_json(ANNOUNCEMENTS_FILE, [])

def add_announcement(title, content, author_name, target_role="All"):
    announcements = load_json(ANNOUNCEMENTS_FILE, [])
    new_item = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "author_name": author_name,
        "target_role": target_role
    }
    announcements.insert(0, new_item)  # Prepend for latest first
    save_json(ANNOUNCEMENTS_FILE, announcements)
    return True

def delete_announcement(announcement_id):
    announcements = load_json(ANNOUNCEMENTS_FILE, [])
    new_items = [a for a in announcements if a["id"] != announcement_id]
    if len(new_items) == len(announcements):
        return False
    save_json(ANNOUNCEMENTS_FILE, new_items)
    return True

# Assignments CRUD Operations
def load_assignments():
    return load_json(ASSIGNMENTS_FILE, [])

def add_assignment(title, description, due_date, class_name, created_by_name, created_by_id):
    assignments = load_json(ASSIGNMENTS_FILE, [])
    new_item = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "due_date": due_date,
        "class_name": class_name,
        "created_by_name": created_by_name,
        "created_by_id": created_by_id,
        "submissions": []
    }
    assignments.insert(0, new_item)
    save_json(ASSIGNMENTS_FILE, assignments)
    return True

def delete_assignment(assignment_id):
    assignments = load_json(ASSIGNMENTS_FILE, [])
    new_items = [a for a in assignments if a["id"] != assignment_id]
    if len(new_items) == len(assignments):
        return False
    save_json(ASSIGNMENTS_FILE, new_items)
    return True

def submit_assignment(assignment_id, student_id, student_name, submission_text):
    assignments = load_json(ASSIGNMENTS_FILE, [])
    for a in assignments:
        if a["id"] == assignment_id:
            # Check if student already submitted
            submissions = a.get("submissions", [])
            existing = next((s for s in submissions if s["student_id"] == student_id), None)
            
            new_submission = {
                "student_id": student_id,
                "student_name": student_name,
                "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "submission_text": submission_text,
                "grade": None,
                "feedback": ""
            }
            
            if existing:
                # Update existing submission
                submissions.remove(existing)
            
            submissions.append(new_submission)
            a["submissions"] = submissions
            save_json(ASSIGNMENTS_FILE, assignments)
            return True
    return False

def grade_submission(assignment_id, student_id, grade, feedback=""):
    assignments = load_json(ASSIGNMENTS_FILE, [])
    for a in assignments:
        if a["id"] == assignment_id:
            for sub in a.get("submissions", []):
                if sub["student_id"] == student_id:
                    sub["grade"] = grade
                    sub["feedback"] = feedback
                    save_json(ASSIGNMENTS_FILE, assignments)
                    return True
    return False

# Attendance CRUD Operations
def load_attendance():
    return load_json(ATTENDANCE_FILE, [])

def mark_attendance(date_str, marked_by_name, records):
    """
    records: Dict of {student_id: status} e.g. {"uuid-1": "Present", "uuid-2": "Absent"}
    """
    attendance = load_json(ATTENDANCE_FILE, [])
    
    # Check if attendance exists for that day, if so, replace it
    existing = next((a for a in attendance if a["date"] == date_str), None)
    
    new_record = {
        "date": date_str,
        "marked_by": marked_by_name,
        "records": records
    }
    
    if existing:
        attendance.remove(existing)
        
    attendance.append(new_record)
    save_json(ATTENDANCE_FILE, attendance)
    return True
