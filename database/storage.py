history = []

def save_record(user, severity):
    history.append({"user": user, "severity": severity})

def get_history():
    return history
