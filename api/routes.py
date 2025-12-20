from flask import Blueprint, request, jsonify
from model.predict import predict_severity
from recommender.diet import diet_plan
from recommender.exercise import exercise_plan
from database.storage import save_record

routes = Blueprint("routes", __name__)

@routes.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    severity = predict_severity(data["image_path"])
    save_record(data["user"], severity)

    return jsonify({
        "severity": severity,
        "diet": diet_plan(severity),
        "exercise": exercise_plan(severity),
        "disclaimer": "Not a medical diagnosis"
    })
