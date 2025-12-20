import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from model.predict import predict_severity
from recommender.diet import diet_plan
from recommender.exercise import exercise_plan
from database.storage import save_record

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
FRONTEND_FOLDER = os.path.join(PROJECT_ROOT, 'frontend')

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

routes = Blueprint("routes", __name__)

# ===== Serve Frontend =====
@routes.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@routes.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)

# ===== API Endpoints =====
@routes.route("/api")
def api_info():
    return jsonify({
        "app": "Osteoarthritis Severity Detection API",
        "endpoints": {
            "POST /analyze": "Analyze X-ray by file path",
            "POST /analyze-upload": "Analyze uploaded X-ray image"
        },
        "status": "running"
    })

@routes.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    severity, confidence = predict_severity(data["image_path"])
    save_record(data["user"], severity)

    return jsonify({
        "severity": severity,
        "confidence": f"{confidence:.2%}",
        "diet": diet_plan(severity),
        "exercise": exercise_plan(severity),
        "disclaimer": "Not a medical diagnosis"
    })

@routes.route("/analyze-upload", methods=["POST"])
def analyze_upload():
    # Check if file was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    user = request.form.get('user', 'anonymous')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Save uploaded file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        # Analyze the image
        severity, confidence = predict_severity(filepath)
        save_record(user, severity)
        
        return jsonify({
            "severity": severity,
            "confidence": f"{confidence:.2%}",
            "diet": diet_plan(severity),
            "exercise": exercise_plan(severity),
            "disclaimer": "Not a medical diagnosis"
        })
    finally:
        # Clean up - remove uploaded file after analysis
        if os.path.exists(filepath):
            os.remove(filepath)
