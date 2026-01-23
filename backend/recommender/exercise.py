def exercise_plan(severity):
    return {
        "Normal": ["Walking"],
        "Mild": ["Stretching"],
        "Moderate": ["Physiotherapy"],
        "Severe": ["Doctor-approved exercises"]
    }.get(severity, [])
