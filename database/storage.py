import os
import random
import string
import hashlib
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING

# Database Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://admin:DTLELproject@patient-cluster.rjadvfw.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = "hospitalDB"

def get_db():
    """Get database connection."""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def init_db():
    """Initialize database indexes."""
    try:
        db = get_db()
        # Create UNIQUE indexes
        db.patients.create_index([("patientId", ASCENDING)], unique=True)
        db.patients.create_index([("whatsappNumber", ASCENDING)], unique=True)
        db.users.create_index([("username", ASCENDING)], unique=True)
        # Session index for expiry could be added here too
        print("✅ Connected to MongoDB and verified indexes!")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")

# Initialize database on module import
init_db()

def generate_patient_id():
    """Generate unique patient ID in format PAT####."""
    db = get_db()
    
    # Find the last created patient ID
    # We sort by length first (implied logic) and then value to handle PAT9 -> PAT10 correctly
    # But MongoDB sort doesn't let us sort by calculated length easily in simple query.
    # However, standard string sort works for fixed length. 
    # For robust "PAT" + number sorting, we might need aggregation, but simple desc sort is usually finding the max.
    
    last_patient = db.patients.find_one(
        {"patientId": {"$regex": "^PAT"}}, 
        sort=[("patientId", DESCENDING)]
    )
    
    if last_patient:
        try:
            last_id = last_patient['patientId']
            last_num = int(last_id.replace("PAT", ""))
            return f"PAT{last_num + 1}"
        except:
            pass
            
    return "PAT1001"

def generate_otp():
    """Generate 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# ===== Patient Management =====

def create_patient(whatsapp_number: str, age: int, past_history: str = "") -> dict:
    print(f"DEBUG: create_patient called with past_history='{past_history}'")
    """
    Create a new patient record.
    Returns the patient dict or None if whatsapp already exists.
    """
    db = get_db()
    
    try:
        # Check if whatsapp already exists
        if db.patients.find_one({"whatsappNumber": whatsapp_number}):
            return None
        
        patient_id = generate_patient_id()
        
        patient_doc = {
            "patientId": patient_id,
            "age": age,
            "whatsappNumber": whatsapp_number,
            "severity": "",
            "pastHistory": past_history,
            "created_at": datetime.utcnow()
        }
        
        db.patients.insert_one(patient_doc)
        
        # Convert _id to string for JSON serialization compatibility if needed
        # But we return specific fields
        
        return {
            "patientId": patient_id,
            "age": age,
            "whatsappNumber": whatsapp_number,
            "severity": "",
            "pastHistory": past_history
        }
    except Exception as e:
        print(f"Error creating patient: {e}")
        return None

def get_patient_by_whatsapp(whatsapp_number: str) -> dict:
    """Get patient by WhatsApp number."""
    db = get_db()
    patient = db.patients.find_one({"whatsappNumber": whatsapp_number}, {"_id": 0})
    return patient

def get_patient_by_id(patient_id: str) -> dict:
    """Get patient by patientId."""
    db = get_db()
    patient = db.patients.find_one({"patientId": patient_id}, {"_id": 0})
    return patient

def update_patient_severity(patient_id: str, severity: str) -> bool:
    """Update patient's severity level after analysis."""
    db = get_db()
    result = db.patients.update_one(
        {"patientId": patient_id},
        {"$set": {"severity": severity}}
    )
    return result.modified_count > 0

def update_patient_history(patient_id: str, past_history: str) -> bool:
    """Update patient's medical history."""
    db = get_db()
    result = db.patients.update_one(
        {"patientId": patient_id},
        {"$set": {"pastHistory": past_history}}
    )
    return result.modified_count > 0

# ===== User Management (Login System) =====

def create_user(username: str, password: str, patient_id: str) -> dict:
    """
    Create a new user account linked to a patient.
    Returns the user dict or None if username exists.
    """
    db = get_db()
    
    try:
        # Check if username already exists
        if db.users.find_one({"username": username}):
            return None
        
        hashed_pw = hash_password(password)
        
        user_doc = {
            "username": username,
            "password": hashed_pw,
            "patientId": patient_id,
            "created_at": datetime.utcnow()
        }
        
        db.users.insert_one(user_doc)
        
        return {
            "username": username,
            "patientId": patient_id
        }
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def verify_user(username: str, password: str) -> dict:
    """
    Verify user credentials.
    Returns user dict (without password) if valid, None otherwise.
    """
    db = get_db()
    hashed_pw = hash_password(password)
    
    user = db.users.find_one(
        {"username": username, "password": hashed_pw},
        {"_id": 0, "password": 0} # Exclude _id and password
    )
    
    return user

def get_user_by_patient_id(patient_id: str) -> dict:
    """Get user by their linked patientId."""
    db = get_db()
    user = db.users.find_one(
        {"patientId": patient_id},
        {"_id": 0, "password": 0}
    )
    return user

# ===== OTP Management =====

def create_otp_session(whatsapp_number: str) -> str:
    """
    Create OTP session for WhatsApp number.
    Returns the generated OTP.
    """
    otp = generate_otp()
    db = get_db()
    
    # Invalidate old OTPs (could just mark them or delete them)
    # Here we can just delete old ones for this number
    db.otp_sessions.delete_many({"whatsappNumber": whatsapp_number})
    
    otp_doc = {
        "whatsappNumber": whatsapp_number,
        "otp": otp,
        "verified": False,
        "created_at": datetime.utcnow()
    }
    
    db.otp_sessions.insert_one(otp_doc)
    return otp

def verify_otp(whatsapp_number: str, otp: str) -> bool:
    """
    Verify OTP for WhatsApp number.
    Returns True if valid, False otherwise.
    """
    db = get_db()
    
    session = db.otp_sessions.find_one({
        "whatsappNumber": whatsapp_number,
        "otp": otp,
        "verified": False
    })
    
    if session:
        # Mark as verified
        db.otp_sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"verified": True}}
        )
        return True
        
    return False

# ===== Signup Flow (Unchanged logic, just different backend calls which are handled above) =====

def signup_patient(whatsapp_number: str, username: str, password: str, age: int, past_history: str = "") -> dict:
    """
    Complete signup: create patient and user account.
    Returns patient and user info or error.
    """
    # Check if whatsapp already registered
    existing_patient = get_patient_by_whatsapp(whatsapp_number)
    if existing_patient:
        return {"error": "WhatsApp number already registered"}
    
    # Check if username taken
    db = get_db()
    # Manual check to fail fast before creating patient
    if db.users.find_one({"username": username}):
        return {"error": "Username already taken"}
    
    # Create patient
    patient = create_patient(whatsapp_number, age, past_history)
    if not patient:
        return {"error": "Failed to create patient"}
    
    # Create user account
    user = create_user(username, password, patient["patientId"])
    if not user:
        # Rollback patient creation
        db.patients.delete_one({"patientId": patient["patientId"]})
        return {"error": "Failed to create user account"}
    
    # Generate OTP for verification
    otp = create_otp_session(whatsapp_number)
    
    return {
        "patient": patient,
        "user": user,
        "otp": otp
    }

# ===== Login Flow (Unchanged logic) =====

def login_with_password(username: str, password: str) -> dict:
    """Login with username and password."""
    user = verify_user(username, password)
    if not user:
        return {"error": "Invalid username or password"}
    
    patient = get_patient_by_id(user["patientId"])
    return {
        "user": user,
        "patient": patient
    }

def login_with_otp(whatsapp_number: str, otp: str) -> dict:
    """Login with WhatsApp number and OTP."""
    if not verify_otp(whatsapp_number, otp):
        return {"error": "Invalid or expired OTP"}
    
    patient = get_patient_by_whatsapp(whatsapp_number)
    if not patient:
        return {"error": "Patient not found"}
    
    user = get_user_by_patient_id(patient["patientId"])
    
    return {
        "patient": patient,
        "user": user
    }

# ===== Legacy compatibility =====

history = []

def save_record(user, severity):
    """Legacy function for backward compatibility."""
    history.append({"user": user, "severity": severity})

def get_history():
    """Legacy function for backward compatibility."""
    return history
