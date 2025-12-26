import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import random
import string
import hashlib

# MongoDB Atlas connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://admin:DTLELproject@patient-cluster.rjadvfw.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = "hospitalDB"

# Create MongoDB client with Atlas-compatible settings
try:
    client = MongoClient(
        MONGO_URI,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=5000
    )
    
    # Test the connection
    client.admin.command('ping')
    print(f"✅ Connected to MongoDB Atlas successfully!")
    
except Exception as e:
    print(f"⚠️ MongoDB connection error: {e}")
    print("⚠️ Running in offline mode - data will not be persisted")
    client = None

# Get database
db = client[DB_NAME] if client else None

# Collections matching your schema
patients_collection = db["patients"] if db else None
users_collection = db["users"] if db else None
otp_collection = db["otp_sessions"] if db else None


def generate_patient_id():
    """Generate unique patient ID in format PAT####."""
    if not patients_collection:
        return f"PAT{random.randint(1000, 9999)}"
    
    # Find the highest patient ID number
    last_patient = patients_collection.find_one(
        {"patientId": {"$regex": "^PAT"}},
        sort=[("patientId", -1)]
    )
    
    if last_patient and "patientId" in last_patient:
        try:
            last_num = int(last_patient["patientId"].replace("PAT", ""))
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
    """
    Create a new patient record.
    Returns the patient document or None if whatsapp already exists.
    """
    if not patients_collection:
        patient_id = generate_patient_id()
        return {
            "patientId": patient_id,
            "age": age,
            "whatsappNumber": whatsapp_number,
            "severity": "",
            "pastHistory": past_history,
        }
    
    # Check if whatsapp already exists
    existing = patients_collection.find_one({"whatsappNumber": whatsapp_number})
    if existing:
        return None
    
    patient_id = generate_patient_id()
    
    patient = {
        "patientId": patient_id,
        "age": age,
        "whatsappNumber": whatsapp_number,
        "severity": "",
        "pastHistory": past_history,
    }
    
    patients_collection.insert_one(patient)
    patient.pop("_id", None)
    return patient


def get_patient_by_whatsapp(whatsapp_number: str) -> dict:
    """Get patient by WhatsApp number."""
    if not patients_collection:
        return None
    
    patient = patients_collection.find_one({"whatsappNumber": whatsapp_number})
    if patient:
        patient.pop("_id", None)
    return patient


def get_patient_by_id(patient_id: str) -> dict:
    """Get patient by patientId."""
    if not patients_collection:
        return None
    
    patient = patients_collection.find_one({"patientId": patient_id})
    if patient:
        patient.pop("_id", None)
    return patient


def update_patient_severity(patient_id: str, severity: str) -> bool:
    """Update patient's severity level after analysis."""
    if not patients_collection:
        return False
    
    result = patients_collection.update_one(
        {"patientId": patient_id},
        {"$set": {"severity": severity}}
    )
    return result.modified_count > 0


def update_patient_history(patient_id: str, past_history: str) -> bool:
    """Update patient's medical history."""
    if not patients_collection:
        return False
    
    result = patients_collection.update_one(
        {"patientId": patient_id},
        {"$set": {"pastHistory": past_history}}
    )
    return result.modified_count > 0


# ===== User Management (Login System) =====

def create_user(username: str, password: str, patient_id: str) -> dict:
    """
    Create a new user account linked to a patient.
    Returns the user document or None if username exists.
    """
    if not users_collection:
        return {"username": username, "patientId": patient_id}
    
    # Check if username already exists
    existing = users_collection.find_one({"username": username})
    if existing:
        return None
    
    user = {
        "username": username,
        "password": hash_password(password),
        "patientId": patient_id,
    }
    
    users_collection.insert_one(user)
    user.pop("_id", None)
    user.pop("password", None)  # Don't return password
    return user


def verify_user(username: str, password: str) -> dict:
    """
    Verify user credentials.
    Returns user document (without password) if valid, None otherwise.
    """
    if not users_collection:
        return None
    
    user = users_collection.find_one({
        "username": username,
        "password": hash_password(password)
    })
    
    if user:
        user.pop("_id", None)
        user.pop("password", None)
        return user
    
    return None


def get_user_by_patient_id(patient_id: str) -> dict:
    """Get user by their linked patientId."""
    if not users_collection:
        return None
    
    user = users_collection.find_one({"patientId": patient_id})
    if user:
        user.pop("_id", None)
        user.pop("password", None)
    return user


# ===== OTP Management =====

def create_otp_session(whatsapp_number: str) -> str:
    """
    Create OTP session for WhatsApp number.
    Returns the generated OTP.
    """
    otp = generate_otp()
    
    if not otp_collection:
        return otp
    
    # Remove any existing OTP for this number
    otp_collection.delete_many({"whatsappNumber": whatsapp_number})
    
    # Create new OTP session
    otp_session = {
        "whatsappNumber": whatsapp_number,
        "otp": otp,
        "created_at": datetime.utcnow(),
        "verified": False
    }
    
    otp_collection.insert_one(otp_session)
    return otp


def verify_otp(whatsapp_number: str, otp: str) -> bool:
    """
    Verify OTP for WhatsApp number.
    Returns True if valid, False otherwise.
    """
    if not otp_collection:
        # In offline mode, accept any 6-digit OTP for testing
        return len(otp) == 6
    
    session = otp_collection.find_one({
        "whatsappNumber": whatsapp_number, 
        "otp": otp, 
        "verified": False
    })
    
    if session:
        # Mark as verified
        otp_collection.update_one(
            {"_id": session["_id"]},
            {"$set": {"verified": True}}
        )
        return True
    
    return False


# ===== Signup Flow =====

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
    if users_collection:
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            return {"error": "Username already taken"}
    
    # Create patient
    patient = create_patient(whatsapp_number, age, past_history)
    if not patient:
        return {"error": "Failed to create patient"}
    
    # Create user account
    user = create_user(username, password, patient["patientId"])
    if not user:
        return {"error": "Failed to create user account"}
    
    # Generate OTP for verification
    otp = create_otp_session(whatsapp_number)
    
    return {
        "patient": patient,
        "user": user,
        "otp": otp  # Remove in production - send via WhatsApp
    }


# ===== Login Flow =====

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
