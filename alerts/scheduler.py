import schedule, time, threading

def notify(msg):
    print("🔔", msg)

def setup_alerts(meds, exercise):
    for t in meds:
        schedule.every().day.at(t).do(notify, "Take medicine")
    schedule.every().day.at(exercise).do(notify, "Exercise time")

def run():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start():
    threading.Thread(target=run, daemon=True).start()
