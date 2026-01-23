def diet_plan(severity):
    plans = {
        "Normal": ["Balanced diet", "Hydration"],
        "Doubtful": ["Anti-inflammatory foods"],
        "Mild": ["Calcium", "Omega-3"],
        "Moderate": ["Protein rich", "Low sugar"],
        "Severe": ["Strict diet", "Medical supervision"]
    }
    return plans.get(severity, [])
