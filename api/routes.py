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
    save_patient_calendar,
    get_patient_calendar,
    add_calendar_event,
    update_calendar_event,
    delete_calendar_event,
)
from services.ollama_service import generate_recommendations, generate_personalized_calendar

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
FRONTEND_FOLDER = os.path.join(PROJECT_ROOT, 'frontend', 'dist')

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
    print(f"DEBUG: signup received data: {data}")
    
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
    """Analyze uploaded X-ray image with personalized recommendations."""
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
        
        # Get patient data for personalized recommendations
        patient_data = None
        if patient_id:
            patient = get_patient_by_id(patient_id)
            if patient:
                patient_data = {
                    "age": patient.get("age"),
                    "pastHistory": patient.get("pastHistory", "")
                }
                update_patient_severity(patient_id, severity)
        
        # Get AI-powered personalized recommendations
        recommendations = generate_recommendations(severity, patient_data)
        
        # Save calendar events to database
        if patient_id and recommendations.get("recommendations", {}).get("alerts"):
            alerts = recommendations["recommendations"]["alerts"]
            # Add event metadata
            for alert in alerts:
                if 'eventId' not in alert:
                    alert['eventId'] = str(uuid.uuid4())
                alert['isAiGenerated'] = True
                alert['isModified'] = False
            save_patient_calendar(patient_id, alerts)
        
        return jsonify({
            "severity": severity,
            "confidence": f"{confidence:.2%}",
            "diet": recommendations["recommendations"].get("diet", []),
            "exercise": recommendations["recommendations"].get("exercise", []),
            "alerts": recommendations["recommendations"].get("alerts", []),
            "source": recommendations.get("source", "static"),
            "personalized": recommendations.get("personalized", False),
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
    patient_id = data.get("patient_id")
    
    # Get patient data for personalization
    patient_data = None
    if patient_id:
        patient = get_patient_by_id(patient_id)
        if patient:
            patient_data = {
                "age": patient.get("age"),
                "pastHistory": patient.get("pastHistory", "")
            }
    
    recommendations = generate_recommendations(severity, patient_data)
    return jsonify(recommendations)


# ===== Calendar Endpoints =====

@routes.route("/api/calendar/<patient_id>", methods=["GET"])
@cross_origin()
def get_calendar(patient_id):
    """Get patient's saved calendar events."""
    calendar = get_patient_calendar(patient_id)
    
    if not calendar:
        return jsonify({"events": [], "patientId": patient_id})
    
    return jsonify(calendar)


@routes.route("/api/calendar/generate", methods=["POST"])
@cross_origin()
def generate_calendar():
    """Generate AI calendar based on patient profile."""
    data = request.json
    patient_id = data.get("patient_id")
    
    if not patient_id:
        return jsonify({"error": "Patient ID required"}), 400
    
    patient = get_patient_by_id(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    severity = patient.get("severity", "Normal")
    if not severity:
        return jsonify({"error": "Please analyze an X-ray first to get a severity level"}), 400
    
    patient_data = {
        "age": patient.get("age"),
        "pastHistory": patient.get("pastHistory", "")
    }
    
    # Generate personalized calendar
    events = generate_personalized_calendar(severity, patient_data)
    
    # Save to database
    save_patient_calendar(patient_id, events)
    
    return jsonify({
        "message": "Calendar generated successfully",
        "events": events,
        "patientId": patient_id,
        "severity": severity
    })


@routes.route("/api/calendar/event", methods=["POST"])
@cross_origin()
def add_event():
    """Add a custom event to patient's calendar."""
    data = request.json
    patient_id = data.get("patient_id")
    event = data.get("event")
    
    if not patient_id or not event:
        return jsonify({"error": "Patient ID and event data required"}), 400
    
    result = add_calendar_event(patient_id, event)
    
    if result:
        return jsonify({"message": "Event added", "event": result}), 201
    return jsonify({"error": "Failed to add event"}), 500


@routes.route("/api/calendar/event/<event_id>", methods=["PUT"])
@cross_origin()
def update_event(event_id):
    """Update an existing calendar event."""
    data = request.json
    patient_id = data.get("patient_id")
    updated_event = data.get("event")
    
    if not patient_id or not updated_event:
        return jsonify({"error": "Patient ID and event data required"}), 400
    
    success = update_calendar_event(patient_id, event_id, updated_event)
    
    if success:
        return jsonify({"message": "Event updated"})
    return jsonify({"error": "Failed to update event"}), 500


@routes.route("/api/calendar/event/<event_id>", methods=["DELETE"])
@cross_origin()
def remove_event(event_id):
    """Delete a calendar event."""
    patient_id = request.args.get("patient_id")
    
    if not patient_id:
        return jsonify({"error": "Patient ID required"}), 400
    
    success = delete_calendar_event(patient_id, event_id)
    
    if success:
        return jsonify({"message": "Event deleted"})
    return jsonify({"error": "Failed to delete event"}), 500

