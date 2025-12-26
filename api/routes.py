import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from flask_cors import cross_origin
from model.predict import predict_severity
from recommender.diet import diet_plan
from recommender.exercise import exercise_plan
from database.storage import (
    signup_patient,
    login_with_password,
    login_with_otp,
    create_otp_session,
    get_patient_by_id,
    get_patient_by_whatsapp,
    update_patient_severity,
)
from services.ollama_service import generate_recommendations

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
FRONTEND_FOLDER = os.path.join(PROJECT_ROOT, 'frontend-react', 'dist')

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

routes = Blueprint("routes", __name__)

# ===== Serve Frontend =====
@routes.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@routes.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)

# ===== API Info =====
@routes.route("/api")
def api_info():
    return jsonify({
        "app": "Osteoarthritis Severity Detection API",
        "endpoints": {
            "POST /api/auth/signup": "Create account (username, password, whatsappNumber, age, pastHistory)",
            "POST /api/auth/login": "Login with username and password",
            "POST /api/auth/send-otp": "Send OTP to WhatsApp",
            "POST /api/auth/verify-otp": "Verify OTP and login",
            "GET /api/patient/<id>": "Get patient details",
            "POST /analyze-upload": "Analyze uploaded X-ray image"
        },
        "status": "running"
    })

# ===== Authentication Endpoints =====

@routes.route("/api/auth/signup", methods=["POST"])
@cross_origin()
def signup():
    """
    Create a new patient and user account.
    Required: whatsappNumber, username, password, age
    Optional: pastHistory
    """
    data = request.json
    
    # Validate required fields
    required_fields = ["whatsappNumber", "username", "password", "age"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    whatsapp_number = data["whatsappNumber"]
    username = data["username"]
    password = data["password"]
    age = int(data["age"])
    past_history = data.get("pastHistory", "")
    
    # Validate whatsapp format (basic validation)
    if len(whatsapp_number) < 10:
        return jsonify({"error": "Invalid WhatsApp number"}), 400
    
    # Signup
    result = signup_patient(whatsapp_number, username, password, age, past_history)
    
    if "error" in result:
        return jsonify(result), 409
    
    return jsonify({
        "message": "Account created successfully",
        "patient": result["patient"],
        "user": result["user"],
        "otp": result.get("otp")  # For development only
    }), 201


@routes.route("/api/auth/login", methods=["POST"])
@cross_origin()
def login():
    """
    Login with username and password.
    Required: username, password
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    result = login_with_password(username, password)
    
    if "error" in result:
        return jsonify(result), 401
    
    return jsonify({
        "message": "Login successful",
        "patient": result["patient"],
        "user": result["user"]
    })


@routes.route("/api/auth/send-otp", methods=["POST"])
@cross_origin()
def send_otp():
    """
    Send OTP to WhatsApp number for login.
    Required: whatsappNumber
    """
    data = request.json
    whatsapp_number = data.get("whatsappNumber")
    
    if not whatsapp_number:
        return jsonify({"error": "WhatsApp number is required"}), 400
    
    # Check if patient exists
    patient = get_patient_by_whatsapp(whatsapp_number)
    if not patient:
        return jsonify({"error": "WhatsApp number not registered"}), 404
    
    # Generate and store OTP
    otp = create_otp_session(whatsapp_number)
    
    # In production, send OTP via WhatsApp API
    return jsonify({
        "message": "OTP sent successfully",
        "whatsappNumber": whatsapp_number,
        "otp": otp  # Remove in production!
    })


@routes.route("/api/auth/verify-otp", methods=["POST"])
@cross_origin()
def verify_otp_endpoint():
    """
    Verify OTP and login.
    Required: whatsappNumber, otp
    """
    data = request.json
    whatsapp_number = data.get("whatsappNumber")
    otp = data.get("otp")
    
    if not whatsapp_number or not otp:
        return jsonify({"error": "WhatsApp number and OTP are required"}), 400
    
    result = login_with_otp(whatsapp_number, otp)
    
    if "error" in result:
        return jsonify(result), 401
    
    return jsonify({
        "message": "Login successful",
        "patient": result["patient"],
        "user": result.get("user")
    })


# ===== Patient Endpoints =====

@routes.route("/api/patient/<patient_id>", methods=["GET"])
@cross_origin()
def get_patient(patient_id):
    """Get patient details by patientId."""
    patient = get_patient_by_id(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    return jsonify({"patient": patient})


# ===== Analysis Endpoints =====

@routes.route("/analyze", methods=["POST"])
@cross_origin()
def analyze():
    """Analyze X-ray by file path."""
    data = request.json
    severity, confidence = predict_severity(data["image_path"])
    patient_id = data.get("patient_id")
    
    # Get AI-powered recommendations
    recommendations = generate_recommendations(severity)
    
    # Update patient severity if patient_id provided
    if patient_id:
        update_patient_severity(patient_id, severity)
    
    return jsonify({
        "severity": severity,
        "confidence": f"{confidence:.2%}",
        "diet": recommendations["recommendations"].get("diet", diet_plan(severity)),
        "exercise": recommendations["recommendations"].get("exercise", []),
        "alerts": recommendations["recommendations"].get("alerts", []),
        "source": recommendations.get("source", "static"),
        "disclaimer": recommendations.get("disclaimer", "Not a medical diagnosis")
    })


@routes.route("/analyze-upload", methods=["POST"])
@cross_origin()
def analyze_upload():
    """Analyze uploaded X-ray image."""
    # Check if file was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    patient_id = request.form.get('patient_id')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Save uploaded file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        # Analyze the image
        severity, confidence = predict_severity(filepath)
        
        # Get AI-powered recommendations
        recommendations = generate_recommendations(severity)
        
        # Update patient severity in database
        if patient_id:
            update_patient_severity(patient_id, severity)
        
        return jsonify({
            "severity": severity,
            "confidence": f"{confidence:.2%}",
            "diet": recommendations["recommendations"].get("diet", []),
            "exercise": recommendations["recommendations"].get("exercise", []),
            "alerts": recommendations["recommendations"].get("alerts", []),
            "source": recommendations.get("source", "static"),
            "disclaimer": recommendations.get("disclaimer", "Not a medical diagnosis")
        })
    finally:
        # Clean up - remove uploaded file after analysis
        if os.path.exists(filepath):
            os.remove(filepath)


# ===== AI Recommendations Endpoint =====
@routes.route("/api/recommendations", methods=["POST"])
@cross_origin()
def get_recommendations():
    """Get AI-powered recommendations for a severity level."""
    data = request.json
    severity = data.get("severity", "Normal")
    
    recommendations = generate_recommendations(severity)
    return jsonify(recommendations)
