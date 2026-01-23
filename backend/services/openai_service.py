import os
import json
import uuid
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Fallback recommendations when OpenAI is unavailable (with Kannada translations)
FALLBACK_RECOMMENDATIONS = {
    "Normal": {
        "diet": [
            {"category": "Anti-inflammatory Foods", "category_kn": "ಉರಿಯೂತ ವಿರೋಧಿ ಆಹಾರಗಳು", "items": ["Fatty fish (salmon, mackerel)", "Leafy greens", "Berries", "Olive oil"], "items_kn": ["ಕೊಬ್ಬಿನ ಮೀನು (ಸಾಲ್ಮನ್, ಮ್ಯಾಕರೆಲ್)", "ಎಲೆಗಳ ತರಕಾರಿಗಳು", "ಬೆರ್ರಿಗಳು", "ಆಲಿವ್ ಎಣ್ಣೆ"], "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ"},
            {"category": "Hydration", "category_kn": "ಜಲಸಂಚಯನ", "items": ["Water (8-10 glasses)", "Green tea", "Bone broth"], "items_kn": ["ನೀರು (8-10 ಗ್ಲಾಸ್)", "ಹಸಿರು ಚಹಾ", "ಮೂಳೆ ಸಾರು"], "frequency": "Throughout the day", "frequency_kn": "ದಿನವಿಡೀ"},
            {"category": "Joint Health", "category_kn": "ಕೀಲು ಆರೋಗ್ಯ", "items": ["Nuts and seeds", "Turmeric", "Ginger"], "items_kn": ["ಬೀಜಗಳು ಮತ್ತು ಒಣಹಣ್ಣುಗಳು", "ಅರಿಶಿನ", "ಶುಂಠಿ"], "frequency": "3-4 times per week", "frequency_kn": "ವಾರಕ್ಕೆ 3-4 ಬಾರಿ"}
        ],
        "exercise": [
            {"name": "Walking", "name_kn": "ನಡಿಗೆ", "duration": "30 minutes", "duration_kn": "30 ನಿಮಿಷಗಳು", "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ", "intensity": "Moderate", "intensity_kn": "ಮಧ್ಯಮ", "tips": "Maintain good posture, wear supportive shoes", "tips_kn": "ಉತ್ತಮ ಭಂಗಿಯನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ, ಬೆಂಬಲಿತ ಬೂಟುಗಳನ್ನು ಧರಿಸಿ"},
            {"name": "Swimming", "name_kn": "ಈಜು", "duration": "20-30 minutes", "duration_kn": "20-30 ನಿಮಿಷಗಳು", "frequency": "3 times/week", "frequency_kn": "ವಾರಕ್ಕೆ 3 ಬಾರಿ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Great for joint mobility without impact", "tips_kn": "ಪ್ರಭಾವವಿಲ್ಲದೆ ಕೀಲುಗಳ ಚಲನಶೀಲತೆಗೆ ಉತ್ತಮ"},
            {"name": "Stretching", "name_kn": "ಹಿಗ್ಗಿಸುವಿಕೆ", "duration": "10-15 minutes", "duration_kn": "10-15 ನಿಮಿಷಗಳು", "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Focus on leg and hip flexibility", "tips_kn": "ಕಾಲು ಮತ್ತು ಸೊಂಟದ ನಮ್ಯತೆಯ ಮೇಲೆ ಗಮನ ಹರಿಸಿ"}
        ],
        "alerts": [
            {"type": "exercise", "title": "Morning Walk", "title_kn": "ಬೆಳಗಿನ ನಡಿಗೆ", "time": "07:00", "frequency": "daily", "description": "30-minute walk to maintain joint health", "description_kn": "ಕೀಲು ಆರೋಗ್ಯವನ್ನು ಕಾಪಾಡಲು 30 ನಿಮಿಷ ನಡಿಗೆ"},
            {"type": "hydration", "title": "Hydration Check", "title_kn": "ನೀರು ಕುಡಿಯಿರಿ", "time": "10:00", "frequency": "daily", "description": "Drink water and stay hydrated", "description_kn": "ನೀರು ಕುಡಿಯಿರಿ ಮತ್ತು ಜಲಸಂಚಯನವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ"},
            {"type": "meal", "title": "Anti-inflammatory Lunch", "title_kn": "ಉರಿಯೂತ ವಿರೋಧಿ ಊಟ", "time": "13:00", "frequency": "daily", "description": "Include leafy greens and omega-3 rich foods", "description_kn": "ಎಲೆಗಳ ತರಕಾರಿಗಳು ಮತ್ತು ಒಮೆಗಾ-3 ಶ್ರೀಮಂತ ಆಹಾರಗಳನ್ನು ಸೇರಿಸಿ"}
        ]
    },
    "Doubtful": {
        "diet": [
            {"category": "Anti-inflammatory Foods", "category_kn": "ಉರಿಯೂತ ವಿರೋಧಿ ಆಹಾರಗಳು", "items": ["Salmon", "Sardines", "Walnuts", "Flaxseeds"], "items_kn": ["ಸಾಲ್ಮನ್", "ಸಾರ್ಡೀನ್ಗಳು", "ಅಕ್ರೋಟು", "ಅಗಸೆ ಬೀಜಗಳು"], "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ"},
            {"category": "Calcium-Rich Foods", "category_kn": "ಕ್ಯಾಲ್ಸಿಯಂ ಶ್ರೀಮಂತ ಆಹಾರಗಳು", "items": ["Low-fat dairy", "Fortified plant milk", "Leafy greens"], "items_kn": ["ಕಡಿಮೆ ಕೊಬ್ಬಿನ ಹಾಲಿನ ಉತ್ಪನ್ನಗಳು", "ಪೋಷಕಾಂಶ ಸೇರಿಸಿದ ಸಸ್ಯ ಹಾಲು", "ಎಲೆಗಳ ತರಕಾರಿಗಳು"], "frequency": "2-3 servings daily", "frequency_kn": "ದಿನಕ್ಕೆ 2-3 ಬಾರಿ"},
            {"category": "Avoid", "category_kn": "ತಪ್ಪಿಸಿ", "items": ["Processed foods", "Excess sugar", "Red meat"], "items_kn": ["ಸಂಸ್ಕರಿಸಿದ ಆಹಾರಗಳು", "ಹೆಚ್ಚಿನ ಸಕ್ಕರೆ", "ಕೆಂಪು ಮಾಂಸ"], "frequency": "Limit intake", "frequency_kn": "ಸೇವನೆ ಮಿತಿಗೊಳಿಸಿ"}
        ],
        "exercise": [
            {"name": "Gentle Yoga", "name_kn": "ಮೃದು ಯೋಗ", "duration": "20-30 minutes", "duration_kn": "20-30 ನಿಮಿಷಗಳು", "frequency": "4 times/week", "frequency_kn": "ವಾರಕ್ಕೆ 4 ಬಾರಿ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Focus on joint-friendly poses", "tips_kn": "ಕೀಲು-ಸ್ನೇಹಿ ಭಂಗಿಗಳ ಮೇಲೆ ಗಮನ ಹರಿಸಿ"},
            {"name": "Cycling", "name_kn": "ಸೈಕ್ಲಿಂಗ್", "duration": "20 minutes", "duration_kn": "20 ನಿಮಿಷಗಳು", "frequency": "3 times/week", "frequency_kn": "ವಾರಕ್ಕೆ 3 ಬಾರಿ", "intensity": "Low-Moderate", "intensity_kn": "ಕಡಿಮೆ-ಮಧ್ಯಮ", "tips": "Use stationary bike for controlled environment", "tips_kn": "ನಿಯಂತ್ರಿತ ಪರಿಸರಕ್ಕಾಗಿ ಸ್ಥಿರ ಸೈಕಲ್ ಬಳಸಿ"},
            {"name": "Water Aerobics", "name_kn": "ನೀರಿನ ಏರೋಬಿಕ್ಸ್", "duration": "30 minutes", "duration_kn": "30 ನಿಮಿಷಗಳು", "frequency": "2 times/week", "frequency_kn": "ವಾರಕ್ಕೆ 2 ಬಾರಿ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Reduces joint stress while building strength", "tips_kn": "ಶಕ್ತಿಯನ್ನು ನಿರ್ಮಿಸುವಾಗ ಕೀಲು ಒತ್ತಡವನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ"}
        ],
        "alerts": [
            {"type": "exercise", "title": "Yoga Session", "title_kn": "ಯೋಗ ಅಭ್ಯಾಸ", "time": "08:00", "frequency": "mon,wed,fri,sat", "description": "Gentle yoga for joint flexibility", "description_kn": "ಕೀಲು ನಮ್ಯತೆಗಾಗಿ ಮೃದು ಯೋಗ"},
            {"type": "medication", "title": "Supplement Reminder", "title_kn": "ಪೂರಕ ನೆನಪು", "time": "09:00", "frequency": "daily", "description": "Take glucosamine/chondroitin if prescribed", "description_kn": "ಸೂಚಿಸಿದ್ದರೆ ಗ್ಲುಕೋಸಮಿನ್/ಕಾಂಡ್ರೊಇಟಿನ್ ತೆಗೆದುಕೊಳ್ಳಿ"},
            {"type": "checkup", "title": "Weekly Joint Check", "title_kn": "ವಾರದ ಕೀಲು ಪರಿಶೀಲನೆ", "time": "18:00", "frequency": "weekly", "description": "Monitor any changes in joint comfort", "description_kn": "ಕೀಲು ಸೌಕರ್ಯದಲ್ಲಿ ಯಾವುದೇ ಬದಲಾವಣೆಗಳನ್ನು ಗಮನಿಸಿ"}
        ]
    },
    "Mild": {
        "diet": [
            {"category": "Omega-3 Rich Foods", "category_kn": "ಒಮೆಗಾ-3 ಶ್ರೀಮಂತ ಆಹಾರಗಳು", "items": ["Fatty fish 3x/week", "Chia seeds", "Hemp seeds", "Algae supplements"], "items_kn": ["ವಾರಕ್ಕೆ 3 ಬಾರಿ ಕೊಬ್ಬಿನ ಮೀನು", "ಚಿಯಾ ಬೀಜಗಳು", "ಹೆಂಪ್ ಬೀಜಗಳು", "ಪಾಚಿ ಪೂರಕಗಳು"], "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ"},
            {"category": "Calcium & Vitamin D", "category_kn": "ಕ್ಯಾಲ್ಸಿಯಂ ಮತ್ತು ವಿಟಮಿನ್ ಡಿ", "items": ["Fortified foods", "Egg yolks", "Mushrooms", "Supplements if needed"], "items_kn": ["ಪೋಷಕಾಂಶ ಸೇರಿಸಿದ ಆಹಾರಗಳು", "ಮೊಟ್ಟೆಯ ಹಳದಿ", "ಅಣಬೆಗಳು", "ಅಗತ್ಯವಿದ್ದರೆ ಪೂರಕಗಳು"], "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ"},
            {"category": "Collagen Support", "category_kn": "ಕೊಲಾಜೆನ್ ಬೆಂಬಲ", "items": ["Bone broth", "Gelatin", "Vitamin C rich fruits"], "items_kn": ["ಮೂಳೆ ಸಾರು", "ಜೆಲಾಟಿನ್", "ವಿಟಮಿನ್ ಸಿ ಶ್ರೀಮಂತ ಹಣ್ಣುಗಳು"], "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ"}
        ],
        "exercise": [
            {"name": "Chair Exercises", "name_kn": "ಕುರ್ಚಿ ವ್ಯಾಯಾಮಗಳು", "duration": "15-20 minutes", "duration_kn": "15-20 ನಿಮಿಷಗಳು", "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Seated leg lifts and stretches", "tips_kn": "ಕುಳಿತು ಕಾಲು ಎತ್ತುವಿಕೆ ಮತ್ತು ಹಿಗ್ಗಿಸುವಿಕೆ"},
            {"name": "Pool Walking", "name_kn": "ಕೊಳದಲ್ಲಿ ನಡಿಗೆ", "duration": "20-30 minutes", "duration_kn": "20-30 ನಿಮಿಷಗಳು", "frequency": "3 times/week", "frequency_kn": "ವಾರಕ್ಕೆ 3 ಬಾರಿ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Water supports joints while providing resistance", "tips_kn": "ನೀರು ಪ್ರತಿರೋಧವನ್ನು ಒದಗಿಸುತ್ತಾ ಕೀಲುಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ"},
            {"name": "Range of Motion", "name_kn": "ಚಲನೆಯ ವ್ಯಾಪ್ತಿ", "duration": "10 minutes", "duration_kn": "10 ನಿಮಿಷಗಳು", "frequency": "Twice daily", "frequency_kn": "ದಿನಕ್ಕೆ ಎರಡು ಬಾರಿ", "intensity": "Very Low", "intensity_kn": "ಬಹಳ ಕಡಿಮೆ", "tips": "Morning and evening to reduce stiffness", "tips_kn": "ಬಿಗಿತನವನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಬೆಳಿಗ್ಗೆ ಮತ್ತು ಸಂಜೆ"}
        ],
        "alerts": [
            {"type": "exercise", "title": "Morning Stretches", "title_kn": "ಬೆಳಗಿನ ಹಿಗ್ಗಿಸುವಿಕೆ", "time": "07:30", "frequency": "daily", "description": "Range of motion exercises to reduce stiffness", "description_kn": "ಬಿಗಿತನವನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಚಲನೆಯ ವ್ಯಾಪ್ತಿ ವ್ಯಾಯಾಮಗಳು"},
            {"type": "medication", "title": "Pain Management", "title_kn": "ನೋವು ನಿರ್ವಹಣೆ", "time": "08:00", "frequency": "daily", "description": "Take prescribed medications with breakfast", "description_kn": "ಉಪಹಾರದೊಂದಿಗೆ ಸೂಚಿಸಿದ ಔಷಧಿಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ"},
            {"type": "exercise", "title": "Pool Session", "title_kn": "ಕೊಳದ ಅಭ್ಯಾಸ", "time": "16:00", "frequency": "mon,wed,fri", "description": "Water-based exercises for joint health", "description_kn": "ಕೀಲು ಆರೋಗ್ಯಕ್ಕಾಗಿ ನೀರು ಆಧಾರಿತ ವ್ಯಾಯಾಮಗಳು"},
            {"type": "checkup", "title": "Monthly Assessment", "title_kn": "ಮಾಸಿಕ ಮೌಲ್ಯಮಾಪನ", "time": "10:00", "frequency": "monthly", "description": "Track progress and symptoms", "description_kn": "ಪ್ರಗತಿ ಮತ್ತು ಲಕ್ಷಣಗಳನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ"}
        ]
    },
    "Moderate": {
        "diet": [
            {"category": "Protein-Rich Foods", "category_kn": "ಪ್ರೋಟೀನ್ ಶ್ರೀಮಂತ ಆಹಾರಗಳು", "items": ["Lean poultry", "Fish", "Legumes", "Tofu"], "items_kn": ["ತೆಳುವಾದ ಕೋಳಿ ಮಾಂಸ", "ಮೀನು", "ದ್ವಿದಳ ಧಾನ್ಯಗಳು", "ಟೋಫು"], "frequency": "Every meal", "frequency_kn": "ಪ್ರತಿ ಊಟದಲ್ಲಿ"},
            {"category": "Low Glycemic Foods", "category_kn": "ಕಡಿಮೆ ಗ್ಲೈಸೆಮಿಕ್ ಆಹಾರಗಳು", "items": ["Whole grains", "Non-starchy vegetables", "Beans"], "items_kn": ["ಪೂರ್ಣ ಧಾನ್ಯಗಳು", "ಪಿಷ್ಟವಿಲ್ಲದ ತರಕಾರಿಗಳು", "ಬೀನ್ಸ್"], "frequency": "Primary carb sources", "frequency_kn": "ಮುಖ್ಯ ಕಾರ್ಬ್ ಮೂಲಗಳು"},
            {"category": "Anti-inflammatory Spices", "category_kn": "ಉರಿಯೂತ ವಿರೋಧಿ ಮಸಾಲೆಗಳು", "items": ["Turmeric with black pepper", "Ginger", "Cinnamon"], "items_kn": ["ಕಪ್ಪು ಮೆಣಸಿನೊಂದಿಗೆ ಅರಿಶಿನ", "ಶುಂಠಿ", "ದಾಲ್ಚಿನಿ"], "frequency": "Daily in meals", "frequency_kn": "ಊಟದಲ್ಲಿ ಪ್ರತಿದಿನ"}
        ],
        "exercise": [
            {"name": "Physiotherapy Exercises", "name_kn": "ಭೌತಚಿಕಿತ್ಸೆ ವ್ಯಾಯಾಮಗಳು", "duration": "30 minutes", "duration_kn": "30 ನಿಮಿಷಗಳು", "frequency": "As prescribed", "frequency_kn": "ಸೂಚಿಸಿದಂತೆ", "intensity": "Customized", "intensity_kn": "ಕಸ್ಟಮೈಸ್ಡ್", "tips": "Follow physiotherapist guidance strictly", "tips_kn": "ಭೌತಚಿಕಿತ್ಸಕರ ಮಾರ್ಗದರ್ಶನವನ್ನು ಕಟ್ಟುನಿಟ್ಟಾಗಿ ಅನುಸರಿಸಿ"},
            {"name": "Isometric Exercises", "name_kn": "ಐಸೋಮೆಟ್ರಿಕ್ ವ್ಯಾಯಾಮಗಳು", "duration": "15 minutes", "duration_kn": "15 ನಿಮಿಷಗಳು", "frequency": "Daily", "frequency_kn": "ಪ್ರತಿದಿನ", "intensity": "Low", "intensity_kn": "ಕಡಿಮೆ", "tips": "Strengthens muscles without moving joints", "tips_kn": "ಕೀಲುಗಳನ್ನು ಚಲಿಸದೆ ಸ್ನಾಯುಗಳನ್ನು ಬಲಪಡಿಸುತ್ತದೆ"},
            {"name": "Tai Chi", "name_kn": "ತಾಯ್ ಚಿ", "duration": "20 minutes", "duration_kn": "20 ನಿಮಿಷಗಳು", "frequency": "3 times/week", "frequency_kn": "ವಾರಕ್ಕೆ 3 ಬಾರಿ", "intensity": "Very Low", "intensity_kn": "ಬಹಳ ಕಡಿಮೆ", "tips": "Improves balance and reduces fall risk", "tips_kn": "ಸಮತೋಲನವನ್ನು ಸುಧಾರಿಸುತ್ತದೆ ಮತ್ತು ಬೀಳುವ ಅಪಾಯವನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ"}
        ],
        "alerts": [
            {"type": "medication", "title": "Morning Medication", "title_kn": "ಬೆಳಗಿನ ಔಷಧಿ", "time": "07:00", "frequency": "daily", "description": "Take prescribed anti-inflammatory medication", "description_kn": "ಸೂಚಿಸಿದ ಉರಿಯೂತ ವಿರೋಧಿ ಔಷಧಿಯನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ"},
            {"type": "exercise", "title": "Physio Exercises", "title_kn": "ಭೌತಚಿಕಿತ್ಸೆ ವ್ಯಾಯಾಮ", "time": "09:00", "frequency": "daily", "description": "Complete prescribed physiotherapy routine", "description_kn": "ಸೂಚಿಸಿದ ಭೌತಚಿಕಿತ್ಸೆ ದಿನಚರಿಯನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ"},
            {"type": "meal", "title": "Anti-inflammatory Meal", "title_kn": "ಉರಿಯೂತ ವಿರೋಧಿ ಊಟ", "time": "12:30", "frequency": "daily", "description": "High protein, low sugar lunch", "description_kn": "ಹೆಚ್ಚಿನ ಪ್ರೋಟೀನ್, ಕಡಿಮೆ ಸಕ್ಕರೆ ಊಟ"},
            {"type": "checkup", "title": "Physio Appointment", "title_kn": "ಭೌತಚಿಕಿತ್ಸೆ ಅಪಾಯಿಂಟ್ಮೆಂಟ್", "time": "14:00", "frequency": "weekly", "description": "Weekly physiotherapy session", "description_kn": "ವಾರದ ಭೌತಚಿಕಿತ್ಸೆ ಅಧಿವೇಶನ"},
            {"type": "medication", "title": "Evening Medication", "title_kn": "ಸಂಜೆ ಔಷಧಿ", "time": "20:00", "frequency": "daily", "description": "Evening pain management if needed", "description_kn": "ಅಗತ್ಯವಿದ್ದರೆ ಸಂಜೆ ನೋವು ನಿರ್ವಹಣೆ"}
        ]
    },
    "Severe": {
        "diet": [
            {"category": "Medical Diet Plan", "category_kn": "ವೈದ್ಯಕೀಯ ಆಹಾರ ಯೋಜನೆ", "items": ["Consult dietitian", "Personalized meal plan", "Monitored intake"], "items_kn": ["ಆಹಾರ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ", "ವೈಯಕ್ತೀಕೃತ ಊಟದ ಯೋಜನೆ", "ಮೇಲ್ವಿಚಾರಣೆಯ ಸೇವನೆ"], "frequency": "As prescribed", "frequency_kn": "ಸೂಚಿಸಿದಂತೆ"},
            {"category": "Weight Management", "category_kn": "ತೂಕ ನಿರ್ವಹಣೆ", "items": ["Calorie-controlled portions", "High fiber foods", "Lean proteins"], "items_kn": ["ಕ್ಯಾಲೊರಿ-ನಿಯಂತ್ರಿತ ಪಾಲುಗಳು", "ಹೆಚ್ಚಿನ ನಾರಿನ ಆಹಾರಗಳು", "ತೆಳುವಾದ ಪ್ರೋಟೀನ್ಗಳು"], "frequency": "Every meal", "frequency_kn": "ಪ್ರತಿ ಊಟದಲ್ಲಿ"},
            {"category": "Supplements", "category_kn": "ಪೂರಕಗಳು", "items": ["Vitamin D3", "Calcium", "Omega-3 (if approved)", "Glucosamine"], "items_kn": ["ವಿಟಮಿನ್ ಡಿ3", "ಕ್ಯಾಲ್ಸಿಯಂ", "ಒಮೆಗಾ-3 (ಅನುಮೋದಿಸಿದರೆ)", "ಗ್ಲುಕೋಸಮಿನ್"], "frequency": "As prescribed by doctor", "frequency_kn": "ವೈದ್ಯರು ಸೂಚಿಸಿದಂತೆ"}
        ],
        "exercise": [
            {"name": "Doctor-Approved Exercises", "name_kn": "ವೈದ್ಯರು ಅನುಮೋದಿಸಿದ ವ್ಯಾಯಾಮಗಳು", "duration": "As tolerated", "duration_kn": "ಸಹಿಸಬಹುದಾದಷ್ಟು", "frequency": "As prescribed", "frequency_kn": "ಸೂಚಿಸಿದಂತೆ", "intensity": "Very Low", "intensity_kn": "ಬಹಳ ಕಡಿಮೆ", "tips": "Only perform exercises approved by orthopedic specialist", "tips_kn": "ಮೂಳೆ ತಜ್ಞರು ಅನುಮೋದಿಸಿದ ವ್ಯಾಯಾಮಗಳನ್ನು ಮಾತ್ರ ಮಾಡಿ"},
            {"name": "Gentle Range of Motion", "name_kn": "ಮೃದು ಚಲನೆಯ ವ್ಯಾಪ್ತಿ", "duration": "5-10 minutes", "duration_kn": "5-10 ನಿಮಿಷಗಳು", "frequency": "2-3 times daily", "frequency_kn": "ದಿನಕ್ಕೆ 2-3 ಬಾರಿ", "intensity": "Minimal", "intensity_kn": "ಕನಿಷ್ಠ", "tips": "Prevent stiffness without causing pain", "tips_kn": "ನೋವು ಉಂಟುಮಾಡದೆ ಬಿಗಿತನವನ್ನು ತಡೆಯಿರಿ"},
            {"name": "Aquatic Therapy", "name_kn": "ಜಲ ಚಿಕಿತ್ಸೆ", "duration": "As prescribed", "duration_kn": "ಸೂಚಿಸಿದಂತೆ", "frequency": "With therapist", "frequency_kn": "ಚಿಕಿತ್ಸಕರೊಂದಿಗೆ", "intensity": "Therapeutic", "intensity_kn": "ಚಿಕಿತ್ಸಾತ್ಮಕ", "tips": "Professional-guided water therapy sessions", "tips_kn": "ವೃತ್ತಿಪರ-ಮಾರ್ಗದರ್ಶಿತ ಜಲ ಚಿಕಿತ್ಸೆ ಅಧಿವೇಶನಗಳು"}
        ],
        "alerts": [
            {"type": "medication", "title": "Morning Medications", "title_kn": "ಬೆಳಗಿನ ಔಷಧಿಗಳು", "time": "07:00", "frequency": "daily", "description": "Take all prescribed medications", "description_kn": "ಎಲ್ಲಾ ಸೂಚಿಸಿದ ಔಷಧಿಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ"},
            {"type": "exercise", "title": "Gentle Movement", "title_kn": "ಮೃದು ಚಲನೆ", "time": "08:30", "frequency": "daily", "description": "Light range of motion exercises", "description_kn": "ಹಗುರವಾದ ಚಲನೆಯ ವ್ಯಾಪ್ತಿ ವ್ಯಾಯಾಮಗಳು"},
            {"type": "medication", "title": "Midday Medication", "title_kn": "ಮಧ್ಯಾಹ್ನ ಔಷಧಿ", "time": "13:00", "frequency": "daily", "description": "Afternoon medication dose", "description_kn": "ಮಧ್ಯಾಹ್ನ ಔಷಧಿ ಡೋಸ್"},
            {"type": "checkup", "title": "Doctor Appointment", "title_kn": "ವೈದ್ಯರ ಅಪಾಯಿಂಟ್ಮೆಂಟ್", "time": "10:00", "frequency": "weekly", "description": "Regular orthopedic follow-up", "description_kn": "ನಿಯಮಿತ ಮೂಳೆ ತಜ್ಞರ ಫಾಲೋ-ಅಪ್"},
            {"type": "exercise", "title": "Aquatic Therapy", "title_kn": "ಜಲ ಚಿಕಿತ್ಸೆ", "time": "15:00", "frequency": "tue,thu", "description": "Supervised water therapy session", "description_kn": "ಮೇಲ್ವಿಚಾರಣೆಯ ಜಲ ಚಿಕಿತ್ಸೆ ಅಧಿವೇಶನ"},
            {"type": "medication", "title": "Evening Medications", "title_kn": "ಸಂಜೆ ಔಷಧಿಗಳು", "time": "20:00", "frequency": "daily", "description": "Night-time medication and pain management", "description_kn": "ರಾತ್ರಿ ಔಷಧಿ ಮತ್ತು ನೋವು ನಿರ್ವಹಣೆ"}
        ]
    }
}

def check_openai_available() -> bool:
    """Check if OpenAI API is available and configured."""
    return bool(OPENAI_API_KEY) and client is not None

def generate_with_openai(prompt: str, system_prompt: str = "") -> str:
    """Generate response using OpenAI."""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"} if "JSON" in (prompt + system_prompt) else None
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return ""

def parse_json_from_response(response: str) -> Dict:
    """Extract JSON from OpenAI response, handling potential markdown blocks."""
    if not response:
        return {}
    
    try:
        # First try direct parsing
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            # Look for JSON between triple backticks
            if "```json" in response:
                content = response.split("```json")[1].split("```")[0].strip()
                return json.loads(content)
            elif "```" in response:
                content = response.split("```")[1].split("```")[0].strip()
                return json.loads(content)
            
            # Find the first { and last }
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            print(f"[RECO] JSON extraction failed: {e}")
    return {}

def generate_recommendations(severity: str, patient_data: dict = None) -> Dict[str, Any]:
    """Generate high-quality, personalized recommendations using OpenAI/GPT-4o mini."""
    print(f"[RECO] Generating for {severity} severity...")
    if check_openai_available():
        patient_context = ""
        if patient_data:
            age = patient_data.get('age', 'unknown')
            past_history = patient_data.get('pastHistory', '')
            patient_context = f"PATIENT CONTEXT: Age: {age} years, Medical History: {past_history if past_history else 'None reported'}."

        system_prompt = """You are a highly experienced Orthopedic Physician and Dietitian specializing in Osteoarthritis management. 
Your goal is to provide specific, medically-accurate, and culturally-relevant advice for Indian patients.
You must respond ONLY with a valid JSON object. No conversational filler."""

        prompt = f"""Based on a patient with {severity.upper()} level knee osteoarthritis, provide a comprehensive management plan.
{patient_context}

The plan must include:
1. DIET: Specific anti-inflammatory foods (like turmeric, ginger, fatty fish) and local Indian grains (Ragi, Jowar).
2. EXERCISE: Joint-friendly activities tailored to the severity (e.g., Isometric quads for moderate/severe, walking for mild).
3. DAILY ALERTS: A structured 7-item daily schedule (Morning meds/exercise, specific meals, hydration, evening stretches).

CRITICAL REQUIREMENT:
- Provide every text field in BOTH English and Kannada (ಕನ್ನಡ).
- Use natural, empathetic Kannada script that an elderly patient can understand.
- Use a JSON structure with "_kn" suffixes for Kannada translations.

JSON STRUCTURE:
{{
    "diet": [
        {{
            "category": "e.g., Anti-inflammatory Foods", 
            "category_kn": "ಉರಿಯೂತ ವಿರೋಧಿ ಆಹಾರಗಳು", 
            "items": ["Specific food 1", "Specific food 2"], 
            "items_kn": ["ನಿರ್ದಿಷ್ಟ ಆಹಾರ 1", "ನಿರ್ದಿಷ್ಟ ಆಹಾರ 2"], 
            "frequency": "e.g., Daily", 
            "frequency_kn": "ಪ್ರತಿದಿನ"
        }}
    ],
    "exercise": [
        {{
            "name": "Exercise Name", 
            "name_kn": "ವ್ಯಾಯಾಮದ ಹೆಸರು", 
            "duration": "Duration", 
            "duration_kn": "ಸಮಯ", 
            "frequency": "Frequency", 
            "frequency_kn": "ಆವರ್ತನ", 
            "intensity": "Intensity", 
            "intensity_kn": "ತೀವ್ರತೆ", 
            "tips": "Safety tips", 
            "tips_kn": "ಸುರಕ್ಷತಾ ಸಲಹೆಗಳು"
        }}
    ],
    "alerts": [
        {{
            "type": "exercise|medication|meal|checkup|hydration", 
            "title": "Alert Title", 
            "title_kn": "ಶೀರ್ಷಿಕೆ", 
            "time": "HH:MM", 
            "frequency": "daily", 
            "description": "Engaging description", 
            "description_kn": "ವಿವರಣೆ"
        }}
    ]
}}

Generate at least 3 diet categories, 3 exercises, and 7 alerts.
Ensure recommendations match the {severity} severity level.
Return ONLY JSON."""

        print("[RECO] Calling OpenAI API...")
        response = generate_with_openai(prompt, system_prompt)
        print(f"[RECO] Raw Response: {response[:500]}...") # Log first 500 chars
        
        parsed = parse_json_from_response(response)
        
        if parsed and all(key in parsed for key in ["diet", "exercise", "alerts"]):
            print("[RECO] Successfully parsed AI recommendations.")
            return {
                "severity": severity,
                "recommendations": parsed,
                "source": "ai",
                "personalized": patient_data is not None,
                "disclaimer": "These AI-generated recommendations are for informational purposes only. Always consult with healthcare professionals."
            }
        else:
            print("[RECO] Failed to parse JSON or keys missing. Falling back.")
    
    print("[RECO] Using fallback recommendations.")
    fallback = FALLBACK_RECOMMENDATIONS.get(severity, FALLBACK_RECOMMENDATIONS["Normal"])
    return {
        "severity": severity,
        "recommendations": fallback,
        "source": "static",
        "personalized": False,
        "disclaimer": "These recommendations are general guidelines. Please consult with healthcare professionals."
    }

def generate_chat_response(message: str, severity: str, patient_data: dict = None) -> Dict[str, str]:
    """Generate empathetic chat response using OpenAI."""
    if not check_openai_available():
        return {"response_kn": "ನಮಸ್ಕಾರ! ನಾನು ಆದಿತ್ಯ.", "response_en": "Hello! I am Aditya."}
    
    patient_context = f"Patient has {severity} severity."
    if patient_data:
        patient_context += f" Age: {patient_data.get('age')}, History: {patient_data.get('pastHistory')}."

    system_prompt = """You are 'Aditya', an empathetic and expert medical AI assistant for osteoarthritis. 
Respond ONLY in JSON format with 'response_kn' and 'response_en' keys. 
Both values MUST be plain strings (no nested objects).
Maintain a supportive, caring tone. Use natural Kannada."""

    prompt = f"""{patient_context}
User says: "{message}"

Provide a helpful, empathetic response. If the user is asking about symptoms or advice, provide specific medical insights based on their severity level.
Keep it concise (2-3 sentences) for voice-readability.
Return ONLY JSON:
{{
    "response_en": "Your English response here (string only)",
    "response_kn": "ನಿಮ್ಮ ಕನ್ನಡ ಪ್ರತಿಕ್ರಿಯೆ ಇಲ್ಲಿ (ಕೇವಲ ಸ್ಟ್ರಿಂಗ್)"
}}"""

    response = generate_with_openai(prompt, system_prompt)
    parsed = parse_json_from_response(response)
    
    # Ensure keys exist and are strings
    res_en = str(parsed.get("response_en", "I apologize, I couldn't process that. Please ask again."))
    res_kn = str(parsed.get("response_kn", "ಕ್ಷಮಿಸಿ, ದಯವಿಟ್ಟು ಇನ್ನೊಮ್ಮೆ ಕೇಳಿ."))
    
    return {"response_en": res_en, "response_kn": res_kn}

def generate_arthritis_chatbot_response(message: str) -> Dict[str, str]:
    """Generate professional arthritis educational insights using OpenAI."""
    if not check_openai_available():
        return {"response_kn": "ಕ್ಷಮಿಸಿ, ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.", "response_en": "Sorry, consult a doctor."}

    system_prompt = """You are 'OsteoBot', a specialist AI educator for Arthritis. 
Respond ONLY in JSON format with 'response_kn' and 'response_en' keys. 
Both values MUST be plain strings.
Provide detailed, evidence-based insights but keep it friendly. Use natural Kannada."""

    prompt = f"""The user is asking: "{message}"

Provide helpful, detailed insights for arthritis management. Include tips on diet, exercise, or lifestyle if relevant.
Ensure the response is high-quality and medically accurate.
Keep the text suitable for text-to-speech (clear and not too long).
Return ONLY JSON:
{{
    "response_en": "Your English insight (string only)",
    "response_kn": "ನಿಮ್ಮ ಕನ್ನಡ ಒಳನೋಟ (ಕೇವಲ ಸ್ಟ್ರಿಂಗ್)"
}}"""

    response = generate_with_openai(prompt, system_prompt)
    parsed = parse_json_from_response(response)

    # Ensure keys exist and are strings
    res_en = str(parsed.get("response_en", "I'm sorry, I cannot provide insights on that at the moment. Please consult a specialist."))
    res_kn = str(parsed.get("response_kn", "ಕ್ಷಮಿಸಿ, ಈ ಬಗ್ಗೆ ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ."))

    return {"response_en": res_en, "response_kn": res_kn}

# Helper functions for routes
def generate_personalized_calendar(severity: str, patient_data: dict) -> List[Dict]:
    res = generate_recommendations(severity, patient_data)
    alerts = res["recommendations"].get("alerts", [])
    for a in alerts:
        a['eventId'] = str(uuid.uuid4())
        a['isAiGenerated'] = True
    return alerts

def get_diet_recommendations(severity: str, patient_data: dict = None) -> List[Dict]:
    return generate_recommendations(severity, patient_data)["recommendations"].get("diet", [])

def get_exercise_plan(severity: str, patient_data: dict = None) -> List[Dict]:
    return generate_recommendations(severity, patient_data)["recommendations"].get("exercise", [])

def get_alert_suggestions(severity: str, patient_data: dict = None) -> List[Dict]:
    return generate_recommendations(severity, patient_data)["recommendations"].get("alerts", [])
