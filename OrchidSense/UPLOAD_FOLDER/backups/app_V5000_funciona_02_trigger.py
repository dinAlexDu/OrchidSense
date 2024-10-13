from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

def job_function():
    print("Hello from the scheduled job!")

scheduler = BackgroundScheduler()
scheduler.add_job(func=job_function, trigger='interval', seconds=5)
scheduler.start()

@app.route('/')
def index():
    return 'Hello, world! Scheduler is running!'

if __name__ == '__main__':
    app.run(use_reloader=False)
