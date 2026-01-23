import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Fallback recommendations when Gemini is unavailable (with Kannada translations)
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


def check_gemini_available() -> bool:
    """Check if Gemini API is available and configured."""
    try:
        if not GEMINI_API_KEY:
            return False
        # Try to list models to verify the API key works
        models = genai.list_models()
        return True
    except Exception as e:
        print(f"Gemini availability check failed: {e}")
        return False


def generate_with_gemini(prompt: str) -> str:
    """Generate response using Gemini."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000,
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return ""


def parse_json_from_response(response: str) -> Dict:
    """Extract JSON from Gemini response."""
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


def generate_recommendations(severity: str, patient_data: dict = None) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on severity level and patient data.
    Uses Gemini if available, falls back to static recommendations.
    
    Args:
        severity: Osteoarthritis severity level
        patient_data: Optional dict with 'age', 'pastHistory' fields
    """
    # Check if Gemini is available
    if check_gemini_available():
        # Build patient context string
        patient_context = ""
        if patient_data:
            age = patient_data.get('age', 'unknown')
            past_history = patient_data.get('pastHistory', '')
            
            patient_context = f"""
PATIENT PROFILE:
- Age: {age} years old
- Medical History: {past_history if past_history else 'No significant history reported'}

IMPORTANT CONSIDERATIONS:
- For older patients (60+): Focus on low-impact exercises, fall prevention, medication timing
- For younger patients: Can include more active exercises but still joint-friendly
- If diabetic: Consider blood sugar impact of diet recommendations, regular meal times
- If heart disease: Avoid strenuous exercises, include medication reminders
- If hypertension: Low-sodium diet recommendations, stress management
"""
        
        prompt = f"""You are a medical AI assistant specializing in osteoarthritis management.
Based on a patient's knee X-ray analysis showing {severity.upper()} severity osteoarthritis, 
generate personalized recommendations in BOTH English AND Kannada (ಕನ್ನಡ).
{patient_context}
Return a valid JSON object with this exact structure (include Kannada translations with "_kn" suffix):
{{
    "diet": [
        {{"category": "Category Name", "category_kn": "ಕನ್ನಡದಲ್ಲಿ ವರ್ಗ", "items": ["item1", "item2"], "items_kn": ["ಐಟಂ1", "ಐಟಂ2"], "frequency": "How often", "frequency_kn": "ಎಷ್ಟು ಬಾರಿ"}}
    ],
    "exercise": [
        {{"name": "Exercise Name", "name_kn": "ವ್ಯಾಯಾಮ ಹೆಸರು", "duration": "Time", "duration_kn": "ಸಮಯ", "frequency": "How often", "frequency_kn": "ಎಷ್ಟು ಬಾರಿ", "intensity": "Level", "intensity_kn": "ಮಟ್ಟ", "tips": "Safety tips", "tips_kn": "ಸುರಕ್ಷತಾ ಸಲಹೆಗಳು"}}
    ],
    "alerts": [
        {{"type": "exercise|medication|meal|checkup|hydration", "title": "Alert Title", "title_kn": "ಎಚ್ಚರಿಕೆ ಶೀರ್ಷಿಕೆ", "time": "HH:MM", "frequency": "daily|weekly|monthly|mon,wed,fri", "description": "Details", "description_kn": "ವಿವರಗಳು"}}
    ]
}}

Consider the severity level ({severity}) when making recommendations:
- Normal: Preventive care, general fitness
- Doubtful: Early intervention, monitoring
- Mild: Active management, lifestyle changes
- Moderate: Medical supervision, physiotherapy
- Severe: Specialist care, restricted activities

Generate a comprehensive daily schedule with at least 5-7 alerts covering:
- Morning exercise routine
- Medication reminders (if applicable based on history)
- Meal times with anti-inflammatory focus
- Hydration reminders
- Evening stretching/relaxation

IMPORTANT: 
- Provide ALL text content in BOTH English AND Kannada
- Use proper Kannada script (ಕನ್ನಡ ಲಿಪಿ) for all Kannada translations
- Make Kannada translations natural and culturally appropriate
- Include local food alternatives where applicable (e.g., ragi, jowar, coconut oil)

Provide practical, actionable recommendations tailored to the patient's age and medical history.
Return ONLY the JSON object, no additional text."""

        response = generate_with_gemini(prompt)
        parsed = parse_json_from_response(response)
        
        if parsed and all(key in parsed for key in ["diet", "exercise", "alerts"]):
            return {
                "severity": severity,
                "recommendations": parsed,
                "source": "ai",
                "personalized": patient_data is not None,
                "disclaimer": "These AI-generated recommendations are for informational purposes only. Always consult with healthcare professionals before making changes to your diet, exercise, or medication regimen."
            }
    
    # Fallback to static recommendations
    fallback = FALLBACK_RECOMMENDATIONS.get(severity, FALLBACK_RECOMMENDATIONS["Normal"])
    return {
        "severity": severity,
        "recommendations": fallback,
        "source": "static",
        "personalized": False,
        "disclaimer": "These recommendations are general guidelines. Please consult with healthcare professionals for personalized medical advice."
    }


def generate_personalized_calendar(severity: str, patient_data: dict) -> List[Dict]:
    """
    Generate a personalized calendar/schedule based on patient data.
    Returns a list of calendar events.
    """
    result = generate_recommendations(severity, patient_data)
    alerts = result["recommendations"].get("alerts", [])
    
    # Add event IDs and metadata
    import uuid
    for alert in alerts:
        alert['eventId'] = str(uuid.uuid4())
        alert['isAiGenerated'] = True
        alert['isModified'] = False
    
    return alerts


def get_diet_recommendations(severity: str, patient_data: dict = None) -> List[Dict]:
    """Get diet recommendations for a severity level."""
    data = generate_recommendations(severity, patient_data)
    return data["recommendations"].get("diet", [])


def get_exercise_plan(severity: str, patient_data: dict = None) -> List[Dict]:
    """Get exercise plan for a severity level."""
    data = generate_recommendations(severity, patient_data)
    return data["recommendations"].get("exercise", [])


def get_alert_suggestions(severity: str, patient_data: dict = None) -> List[Dict]:
    """Get suggested alerts for a severity level."""
    data = generate_recommendations(severity, patient_data)
    return data["recommendations"].get("alerts", [])


def generate_chat_response(message: str, severity: str, patient_data: dict = None) -> Dict[str, str]:
    """
    Generate an AI response for the chat interface in Kannada.
    """
    print(f"[CHAT] Received message: {message}")
    print(f"[CHAT] Severity: {severity}, Patient data: {patient_data}")
    
    # Check if Gemini is available first
    if not GEMINI_API_KEY:
        print("[CHAT] ERROR: No Gemini API key configured!")
        return {
            "response_kn": "ನಮಸ್ಕಾರ! ನಾನು ಆದಿತ್ಯ. ನಿಮ್ಮ ಆರೋಗ್ಯದ ಬಗ್ಗೆ ಕಾಳಜಿ ವಹಿಸಿ. ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ನಿಯಮಿತವಾಗಿ ಭೇಟಿ ಮಾಡಿ.",
            "response_en": "Hello! I am Aditya. Take care of your health. Visit your doctor regularly."
        }
    
    patient_context = ""
    if patient_data:
        age = patient_data.get('age', 'unknown')
        past_history = patient_data.get('pastHistory', '')
        patient_context = f"The patient is {age} years old with a history of: {past_history}."

    prompt = f"""You are 'Aditya', a friendly and empathetic medical AI assistant specializing in osteoarthritis.
Context: The patient has {severity} severity osteoarthritis. {patient_context}

User Message: "{message}"

Task: Respond to the user's message in a helpful, encouraging, and natural way.
Requirements:
1. Provide the response primarily in KANNADA (ಕನ್ನಡ).
2. Use clear, natural, and simple Kannada that is easy for older patients to understand.
3. Keep the response concise (2-3 sentences) so it's suitable for voice output.
4. Also provide a brief English translation.
5. Do NOT give specific medical diagnoses or suggest changing prescribed medications. Always advise consulting their doctor for specific medical changes.

Return ONLY a JSON object:
{{
    "response_kn": "ಕನ್ನಡದಲ್ಲಿ ನಿಮ್ಮ ಉತ್ತರ",
    "response_en": "Your response in English"
}}
"""

    print("[CHAT] Calling Gemini API...")
    response = generate_with_gemini(prompt)
    print(f"[CHAT] Gemini response: {response[:200] if response else 'EMPTY'}...")
    
    parsed = parse_json_from_response(response)
    print(f"[CHAT] Parsed response: {parsed}")
    
    if parsed and "response_kn" in parsed:
        return parsed
    
    # Provide a more helpful fallback based on common greetings
    message_lower = message.lower() if message else ""
    
    if any(word in message_lower for word in ['hello', 'hi', 'namaste', 'ನಮಸ್ಕಾರ', 'ಹಲೋ']):
        return {
            "response_kn": "ನಮಸ್ಕಾರ! ನಾನು ಆದಿತ್ಯ. ನಿಮ್ಮ ಆರೋಗ್ಯದ ಬಗ್ಗೆ ನನಗೆ ಹೇಳಿ. ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ.",
            "response_en": "Hello! I am Aditya. Tell me about your health. I am here to help you."
        }
    elif any(word in message_lower for word in ['pain', 'hurt', 'ನೋವು', 'ವೇದನೆ']):
        return {
            "response_kn": "ನೋವು ಇದ್ದರೆ, ಮೊದಲು ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ. ನೋವು ಮುಂದುವರಿದರೆ, ದಯವಿಟ್ಟು ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ.",
            "response_en": "If you have pain, first take rest. If pain continues, please visit your doctor."
        }
    elif any(word in message_lower for word in ['exercise', 'walk', 'ವ್ಯಾಯಾಮ', 'ನಡಿಗೆ']):
        return {
            "response_kn": "ಹಗುರವಾದ ವ್ಯಾಯಾಮ ಮತ್ತು ನಡಿಗೆ ಕೀಲುಗಳಿಗೆ ಒಳ್ಳೆಯದು. ಆದರೆ ನಿಮ್ಮ ಶಕ್ತಿಗೆ ಅನುಗುಣವಾಗಿ ಮಾಡಿ.",
            "response_en": "Light exercise and walking is good for joints. But do according to your capacity."
        }
    elif any(word in message_lower for word in ['diet', 'food', 'eat', 'ಆಹಾರ', 'ತಿನ್ನು']):
        return {
            "response_kn": "ಆರೋಗ್ಯಕರ ಆಹಾರ ಬಹಳ ಮುಖ್ಯ. ತರಕಾರಿಗಳು, ಹಣ್ಣುಗಳು ಮತ್ತು ಪ್ರೋಟೀನ್ ಸಮೃದ್ಧ ಆಹಾರ ತಿನ್ನಿ.",
            "response_en": "Healthy food is very important. Eat vegetables, fruits and protein-rich food."
        }
    
    return {
        "response_kn": "ನಮಸ್ಕಾರ! ನಾನು ಆದಿತ್ಯ. ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ನನಗೆ ಸಂತೋಷವಾಗುತ್ತದೆ. ದಯವಿಟ್ಟು ಇನ್ನೊಮ್ಮೆ ಕೇಳಿ.",
        "response_en": "Hello! I am Aditya. I would be happy to answer your question. Please ask again."
    }
