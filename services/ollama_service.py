import requests
import json
from typing import Dict, List, Any

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2"  # Change to your preferred model

# Fallback recommendations when Ollama is unavailable
FALLBACK_RECOMMENDATIONS = {
    "Normal": {
        "diet": [
            {"category": "Anti-inflammatory Foods", "items": ["Fatty fish (salmon, mackerel)", "Leafy greens", "Berries", "Olive oil"], "frequency": "Daily"},
            {"category": "Hydration", "items": ["Water (8-10 glasses)", "Green tea", "Bone broth"], "frequency": "Throughout the day"},
            {"category": "Joint Health", "items": ["Nuts and seeds", "Turmeric", "Ginger"], "frequency": "3-4 times per week"}
        ],
        "exercise": [
            {"name": "Walking", "duration": "30 minutes", "frequency": "Daily", "intensity": "Moderate", "tips": "Maintain good posture, wear supportive shoes"},
            {"name": "Swimming", "duration": "20-30 minutes", "frequency": "3 times/week", "intensity": "Low", "tips": "Great for joint mobility without impact"},
            {"name": "Stretching", "duration": "10-15 minutes", "frequency": "Daily", "intensity": "Low", "tips": "Focus on leg and hip flexibility"}
        ],
        "alerts": [
            {"type": "exercise", "title": "Morning Walk", "time": "07:00", "frequency": "daily", "description": "30-minute walk to maintain joint health"},
            {"type": "hydration", "title": "Hydration Check", "time": "10:00", "frequency": "daily", "description": "Drink water and stay hydrated"},
            {"type": "meal", "title": "Anti-inflammatory Lunch", "time": "13:00", "frequency": "daily", "description": "Include leafy greens and omega-3 rich foods"}
        ]
    },
    "Doubtful": {
        "diet": [
            {"category": "Anti-inflammatory Foods", "items": ["Salmon", "Sardines", "Walnuts", "Flaxseeds"], "frequency": "Daily"},
            {"category": "Calcium-Rich Foods", "items": ["Low-fat dairy", "Fortified plant milk", "Leafy greens"], "frequency": "2-3 servings daily"},
            {"category": "Avoid", "items": ["Processed foods", "Excess sugar", "Red meat"], "frequency": "Limit intake"}
        ],
        "exercise": [
            {"name": "Gentle Yoga", "duration": "20-30 minutes", "frequency": "4 times/week", "intensity": "Low", "tips": "Focus on joint-friendly poses"},
            {"name": "Cycling", "duration": "20 minutes", "frequency": "3 times/week", "intensity": "Low-Moderate", "tips": "Use stationary bike for controlled environment"},
            {"name": "Water Aerobics", "duration": "30 minutes", "frequency": "2 times/week", "intensity": "Low", "tips": "Reduces joint stress while building strength"}
        ],
        "alerts": [
            {"type": "exercise", "title": "Yoga Session", "time": "08:00", "frequency": "mon,wed,fri,sat", "description": "Gentle yoga for joint flexibility"},
            {"type": "medication", "title": "Supplement Reminder", "time": "09:00", "frequency": "daily", "description": "Take glucosamine/chondroitin if prescribed"},
            {"type": "checkup", "title": "Weekly Joint Check", "time": "18:00", "frequency": "weekly", "description": "Monitor any changes in joint comfort"}
        ]
    },
    "Mild": {
        "diet": [
            {"category": "Omega-3 Rich Foods", "items": ["Fatty fish 3x/week", "Chia seeds", "Hemp seeds", "Algae supplements"], "frequency": "Daily"},
            {"category": "Calcium & Vitamin D", "items": ["Fortified foods", "Egg yolks", "Mushrooms", "Supplements if needed"], "frequency": "Daily"},
            {"category": "Collagen Support", "items": ["Bone broth", "Gelatin", "Vitamin C rich fruits"], "frequency": "Daily"}
        ],
        "exercise": [
            {"name": "Chair Exercises", "duration": "15-20 minutes", "frequency": "Daily", "intensity": "Low", "tips": "Seated leg lifts and stretches"},
            {"name": "Pool Walking", "duration": "20-30 minutes", "frequency": "3 times/week", "intensity": "Low", "tips": "Water supports joints while providing resistance"},
            {"name": "Range of Motion", "duration": "10 minutes", "frequency": "Twice daily", "intensity": "Very Low", "tips": "Morning and evening to reduce stiffness"}
        ],
        "alerts": [
            {"type": "exercise", "title": "Morning Stretches", "time": "07:30", "frequency": "daily", "description": "Range of motion exercises to reduce stiffness"},
            {"type": "medication", "title": "Pain Management", "time": "08:00", "frequency": "daily", "description": "Take prescribed medications with breakfast"},
            {"type": "exercise", "title": "Pool Session", "time": "16:00", "frequency": "mon,wed,fri", "description": "Water-based exercises for joint health"},
            {"type": "checkup", "title": "Monthly Assessment", "time": "10:00", "frequency": "monthly", "description": "Track progress and symptoms"}
        ]
    },
    "Moderate": {
        "diet": [
            {"category": "Protein-Rich Foods", "items": ["Lean poultry", "Fish", "Legumes", "Tofu"], "frequency": "Every meal"},
            {"category": "Low Glycemic Foods", "items": ["Whole grains", "Non-starchy vegetables", "Beans"], "frequency": "Primary carb sources"},
            {"category": "Anti-inflammatory Spices", "items": ["Turmeric with black pepper", "Ginger", "Cinnamon"], "frequency": "Daily in meals"}
        ],
        "exercise": [
            {"name": "Physiotherapy Exercises", "duration": "30 minutes", "frequency": "As prescribed", "intensity": "Customized", "tips": "Follow physiotherapist guidance strictly"},
            {"name": "Isometric Exercises", "duration": "15 minutes", "frequency": "Daily", "intensity": "Low", "tips": "Strengthens muscles without moving joints"},
            {"name": "Tai Chi", "duration": "20 minutes", "frequency": "3 times/week", "intensity": "Very Low", "tips": "Improves balance and reduces fall risk"}
        ],
        "alerts": [
            {"type": "medication", "title": "Morning Medication", "time": "07:00", "frequency": "daily", "description": "Take prescribed anti-inflammatory medication"},
            {"type": "exercise", "title": "Physio Exercises", "time": "09:00", "frequency": "daily", "description": "Complete prescribed physiotherapy routine"},
            {"type": "meal", "title": "Anti-inflammatory Meal", "time": "12:30", "frequency": "daily", "description": "High protein, low sugar lunch"},
            {"type": "checkup", "title": "Physio Appointment", "time": "14:00", "frequency": "weekly", "description": "Weekly physiotherapy session"},
            {"type": "medication", "title": "Evening Medication", "time": "20:00", "frequency": "daily", "description": "Evening pain management if needed"}
        ]
    },
    "Severe": {
        "diet": [
            {"category": "Medical Diet Plan", "items": ["Consult dietitian", "Personalized meal plan", "Monitored intake"], "frequency": "As prescribed"},
            {"category": "Weight Management", "items": ["Calorie-controlled portions", "High fiber foods", "Lean proteins"], "frequency": "Every meal"},
            {"category": "Supplements", "items": ["Vitamin D3", "Calcium", "Omega-3 (if approved)", "Glucosamine"], "frequency": "As prescribed by doctor"}
        ],
        "exercise": [
            {"name": "Doctor-Approved Exercises", "duration": "As tolerated", "frequency": "As prescribed", "intensity": "Very Low", "tips": "Only perform exercises approved by orthopedic specialist"},
            {"name": "Gentle Range of Motion", "duration": "5-10 minutes", "frequency": "2-3 times daily", "intensity": "Minimal", "tips": "Prevent stiffness without causing pain"},
            {"name": "Aquatic Therapy", "duration": "As prescribed", "frequency": "With therapist", "intensity": "Therapeutic", "tips": "Professional-guided water therapy sessions"}
        ],
        "alerts": [
            {"type": "medication", "title": "Morning Medications", "time": "07:00", "frequency": "daily", "description": "Take all prescribed medications"},
            {"type": "exercise", "title": "Gentle Movement", "time": "08:30", "frequency": "daily", "description": "Light range of motion exercises"},
            {"type": "medication", "title": "Midday Medication", "time": "13:00", "frequency": "daily", "description": "Afternoon medication dose"},
            {"type": "checkup", "title": "Doctor Appointment", "time": "10:00", "frequency": "weekly", "description": "Regular orthopedic follow-up"},
            {"type": "exercise", "title": "Aquatic Therapy", "time": "15:00", "frequency": "tue,thu", "description": "Supervised water therapy session"},
            {"type": "medication", "title": "Evening Medications", "time": "20:00", "frequency": "daily", "description": "Night-time medication and pain management"}
        ]
    }
}


def check_ollama_available() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def generate_with_ollama(prompt: str) -> str:
    """Generate response using Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000
                }
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return ""
    except Exception as e:
        print(f"Ollama error: {e}")
        return ""


def parse_json_from_response(response: str) -> Dict:
    """Extract JSON from Ollama response."""
    try:
        # Try to find JSON in the response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return {}


def generate_recommendations(severity: str) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on severity level.
    Uses Ollama if available, falls back to static recommendations.
    """
    # Check if Ollama is available
    if check_ollama_available():
        prompt = f"""You are a medical AI assistant specializing in osteoarthritis management.
Based on a patient's knee X-ray analysis showing {severity.upper()} severity osteoarthritis, 
generate personalized recommendations.

Return a valid JSON object with this exact structure:
{{
    "diet": [
        {{"category": "Category Name", "items": ["item1", "item2"], "frequency": "How often"}}
    ],
    "exercise": [
        {{"name": "Exercise Name", "duration": "Time", "frequency": "How often", "intensity": "Level", "tips": "Safety tips"}}
    ],
    "alerts": [
        {{"type": "exercise|medication|meal|checkup|hydration", "title": "Alert Title", "time": "HH:MM", "frequency": "daily|weekly|monthly", "description": "Details"}}
    ]
}}

Consider the severity level ({severity}) when making recommendations:
- Normal: Preventive care, general fitness
- Doubtful: Early intervention, monitoring
- Mild: Active management, lifestyle changes
- Moderate: Medical supervision, physiotherapy
- Severe: Specialist care, restricted activities

Provide practical, actionable recommendations. Include at least 3 items for each category.
Return ONLY the JSON object, no additional text."""

        response = generate_with_ollama(prompt)
        parsed = parse_json_from_response(response)
        
        if parsed and all(key in parsed for key in ["diet", "exercise", "alerts"]):
            return {
                "severity": severity,
                "recommendations": parsed,
                "source": "ai",
                "disclaimer": "These AI-generated recommendations are for informational purposes only. Always consult with healthcare professionals before making changes to your diet, exercise, or medication regimen."
            }
    
    # Fallback to static recommendations
    fallback = FALLBACK_RECOMMENDATIONS.get(severity, FALLBACK_RECOMMENDATIONS["Normal"])
    return {
        "severity": severity,
        "recommendations": fallback,
        "source": "static",
        "disclaimer": "These recommendations are general guidelines. Please consult with healthcare professionals for personalized medical advice."
    }


def get_diet_recommendations(severity: str) -> List[Dict]:
    """Get diet recommendations for a severity level."""
    data = generate_recommendations(severity)
    return data["recommendations"].get("diet", [])


def get_exercise_plan(severity: str) -> List[Dict]:
    """Get exercise plan for a severity level."""
    data = generate_recommendations(severity)
    return data["recommendations"].get("exercise", [])


def get_alert_suggestions(severity: str) -> List[Dict]:
    """Get suggested alerts for a severity level."""
    data = generate_recommendations(severity)
    return data["recommendations"].get("alerts", [])
