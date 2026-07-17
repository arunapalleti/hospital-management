import os
import json
import threading
import hashlib

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Thread safety lock
db_lock = threading.Lock()

def get_file_path(table_name):
    """Returns the absolute path for a database file."""
    return os.path.join(DATA_DIR, f"{table_name}.json")

def load_data(table_name):
    """Loads and returns data from the specified table. Thread-safe."""
    file_path = get_file_path(table_name)
    with db_lock:
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception as e:
            print(f"Error loading {table_name}: {e}")
            return []

def save_data(table_name, data):
    """Saves data back to the specified table. Thread-safe."""
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = get_file_path(table_name)
    with db_lock:
        try:
            # Atomic write using a temporary file
            temp_path = file_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, default=str)
            if os.path.exists(file_path):
                os.remove(file_path)
            os.rename(temp_path, file_path)
            return True
        except Exception as e:
            print(f"Error saving {table_name}: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

def insert_record(table_name, record):
    """Inserts a new record into a table."""
    data = load_data(table_name)
    data.append(record)
    save_data(table_name, data)
    return record

def get_record(table_name, record_id, key_name="id"):
    """Fetches a specific record by its unique key."""
    data = load_data(table_name)
    for record in data:
        if str(record.get(key_name)) == str(record_id):
            return record
    return None

def update_record(table_name, record_id, updated_record, key_name="id"):
    """Updates an existing record. Returns True if updated, else False."""
    data = load_data(table_name)
    for i, record in enumerate(data):
        if str(record.get(key_name)) == str(record_id):
            # Maintain ID and update rest
            updated_record[key_name] = record_id
            data[i] = updated_record
            return save_data(table_name, data)
    return False

def delete_record(table_name, record_id, key_name="id"):
    """Deletes a record by its unique key. Returns True if deleted, else False."""
    data = load_data(table_name)
    initial_length = len(data)
    data = [record for record in data if str(record.get(key_name)) != str(record_id)]
    if len(data) < initial_length:
        return save_data(table_name, data)
    return False

def hash_password(password, salt="smart_hospital_salt"):
    """Utility to hash password since we need it for seeding the admin."""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def initialize_databases():
    """Initializes JSON data directories and seeds default records if empty."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Initialize Users (seed admin if empty)
    users_path = get_file_path("users")
    if not os.path.exists(users_path) or load_data("users") == []:
        default_users = [
            {
                "fullname": "System Administrator",
                "username": "admin",
                "email": "admin@smarthospital.com",
                "password": hash_password("admin123"),
                "role": "Admin"
            },
            {
                "fullname": "Dr. Robert Chen",
                "username": "drrobert",
                "email": "robert.chen@smarthospital.com",
                "password": hash_password("doctor123"),
                "role": "Doctor"
            }
        ]
        save_data("users", default_users)
        print("Users initialized with seed accounts: admin/admin123 and drrobert/doctor123")

    # 2. Initialize Doctors
    doctors_path = get_file_path("doctors")
    if not os.path.exists(doctors_path) or load_data("doctors") == []:
        default_doctors = [
            {
                "id": "DOC-101",
                "name": "Dr. Robert Chen",
                "specialization": "General Physician",
                "qualification": "MBBS, MD (General Medicine)",
                "experience": 8,
                "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                "consultation_time": "09:00 - 13:00",
                "phone": "+1-555-0190",
                "email": "robert.chen@smarthospital.com",
                "status": "Available"
            },
            {
                "id": "DOC-102",
                "name": "Dr. Aris Thorne",
                "specialization": "Cardiologist",
                "qualification": "MD (Cardiology), FACC",
                "experience": 12,
                "available_days": ["Mon", "Wed", "Fri"],
                "consultation_time": "10:00 - 13:00",
                "phone": "+1-555-0182",
                "email": "aris.thorne@smarthospital.com",
                "status": "Available"
            },
            {
                "id": "DOC-103",
                "name": "Dr. Sarah Jenkins",
                "specialization": "Neurologist",
                "qualification": "MD, PhD (Neurology)",
                "experience": 15,
                "available_days": ["Tue", "Thu"],
                "consultation_time": "14:00 - 17:00",
                "phone": "+1-555-0174",
                "email": "sarah.jenkins@smarthospital.com",
                "status": "On Leave"
            },
            {
                "id": "DOC-104",
                "name": "Dr. Emily Taylor",
                "specialization": "Pediatrician",
                "qualification": "MD, DCH (Pediatrics)",
                "experience": 10,
                "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "consultation_time": "15:00 - 18:00",
                "phone": "+1-555-0163",
                "email": "emily.taylor@smarthospital.com",
                "status": "Available"
            }
        ]
        save_data("doctors", default_doctors)
        print("Doctors database initialized with default specialist profiles.")

    # 3. Initialize Tablets
    tablets_path = get_file_path("tablets")
    if not os.path.exists(tablets_path) or load_data("tablets") == []:
        default_tablets = [
            {
                "id": "TAB-001",
                "name": "Paracetamol",
                "manufacturer": "PharmaCare Labs",
                "category": "Analgesic / Antipyretic",
                "dosage": "1 tablet every 6 hours as needed",
                "strength": "500mg",
                "price": 0.10,
                "stock": 500,
                "expiry_date": "2027-12-31",
                "uses": "Pain relief, reducing fever",
                "side_effects": "Nausea, liver damage on high overdose"
            },
            {
                "id": "TAB-002",
                "name": "Cetirizine",
                "manufacturer": "AllerShield Inc.",
                "category": "Antihistamine",
                "dosage": "1 tablet daily at bedtime",
                "strength": "10mg",
                "price": 0.15,
                "stock": 15,  # Low stock alert
                "expiry_date": "2026-10-30",
                "uses": "Allergic rhinitis, cold symptoms, sneezing",
                "side_effects": "Drowsiness, dry mouth, tiredness"
            },
            {
                "id": "TAB-003",
                "name": "Metformin",
                "manufacturer": "GlycoPharma Ltd.",
                "category": "Antidiabetic",
                "dosage": "1 tablet twice daily with meals",
                "strength": "500mg",
                "price": 0.25,
                "stock": 300,
                "expiry_date": "2026-08-10",  # Expiring soon
                "uses": "Type-2 Diabetes mellitus management",
                "side_effects": "Nausea, abdominal pain, diarrhea, metallic taste"
            },
            {
                "id": "TAB-004",
                "name": "Amlodipine",
                "manufacturer": "CardioMeds Co.",
                "category": "Antihypertensive",
                "dosage": "1 tablet once daily in the morning",
                "strength": "5mg",
                "price": 0.20,
                "stock": 250,
                "expiry_date": "2028-03-15",
                "uses": "Hypertension, angina chest pain",
                "side_effects": "Ankle swelling, dizziness, flushing, fatigue"
            },
            {
                "id": "TAB-005",
                "name": "Vitamin C",
                "manufacturer": "VitaHealth Supplements",
                "category": "Supplement",
                "dosage": "1 tablet chewable daily",
                "strength": "500mg",
                "price": 0.05,
                "stock": 12,  # Low stock alert
                "expiry_date": "2027-05-20",
                "uses": "Immunity support, vitamin C deficiency",
                "side_effects": "Mild diarrhea if consumed in high quantities"
            }
        ]
        save_data("tablets", default_tablets)
        print("Tablets inventory database initialized.")

    # 4. Initialize Recommendations
    recommendations_path = get_file_path("recommendations")
    if not os.path.exists(recommendations_path) or load_data("recommendations") == []:
        default_recommendations = [
            {
                "disease": "Cold",
                "symptoms": ["cough", "runny nose", "sneezing", "sore throat", "nasal congestion"],
                "tablets": ["Paracetamol", "Cetirizine", "Vitamin C"],
                "dosage": "Cetirizine: 1 tablet daily at night. Paracetamol: 1 tablet every 6 hours if fever. Vitamin C: 1 tablet daily.",
                "precautions": "Avoid cold beverages, rest well, stay hydrated.",
                "side_effects": "Drowsiness (due to Cetirizine), mild dry mouth.",
                "specialist": "General Physician"
            },
            {
                "disease": "Fever",
                "symptoms": ["high body temperature", "chills", "body ache", "sweating", "headache"],
                "tablets": ["Paracetamol"],
                "dosage": "Paracetamol: 500mg 1 tablet every 6 hours. Max 4g daily.",
                "precautions": "Take after meals, do not consume alcohol, monitor temperature.",
                "side_effects": "Rare: mild nausea or skin rash. Avoid double dosage.",
                "specialist": "General Physician"
            },
            {
                "disease": "Headache",
                "symptoms": ["throbbing head pain", "migraine", "tension in temples", "sensitivity to light"],
                "tablets": ["Paracetamol"],
                "dosage": "Paracetamol: 500mg 1 tablet on onset of pain. Repeat after 6 hours if needed.",
                "precautions": "Rest in a quiet, dark room. Limit caffeine intake.",
                "side_effects": "Safe in short term. Avoid long term unprescribed use.",
                "specialist": "Neurologist"
            },
            {
                "disease": "Diabetes",
                "symptoms": ["high blood sugar levels", "frequent urination", "increased thirst", "fatigue"],
                "tablets": ["Metformin"],
                "dosage": "Metformin: 500mg twice daily with meals (breakfast and dinner).",
                "precautions": "Regularly monitor blood sugar. Maintain low-glycemic diet. Keep hydrated.",
                "side_effects": "Stomach upset, metallic taste, nausea, diarrhea (usually temporary).",
                "specialist": "Nephrologist"
            },
            {
                "disease": "Hypertension",
                "symptoms": ["high blood pressure readings", "dizziness", "chest pressure", "shortness of breath"],
                "tablets": ["Amlodipine"],
                "dosage": "Amlodipine: 5mg once daily, preferably in the morning.",
                "precautions": "Monitor blood pressure daily. Restrict table salt intake. Change positions slowly.",
                "side_effects": "Ankle swelling (peripheral edema), fatigue, lightheadedness.",
                "specialist": "Cardiologist"
            }
        ]
        save_data("recommendations", default_recommendations)
        print("Recommendation rules database initialized.")

    # 5. Initialize Patients (empty on start)
    patients_path = get_file_path("patients")
    if not os.path.exists(patients_path):
        save_data("patients", [])

    # 6. Initialize History (empty on start)
    history_path = get_file_path("history")
    if not os.path.exists(history_path):
        save_data("history", [])

if __name__ == "__main__":
    # Test initialization
    initialize_databases()
