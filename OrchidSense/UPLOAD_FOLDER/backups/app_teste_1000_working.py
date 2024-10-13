import logging
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)

# Configuração básica do logging
logging.basicConfig(level=logging.INFO)

def job_function():
    app.logger.info("Hello from the scheduled job!")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_function, 'interval', seconds=5)
    scheduler.start()

@app.route('/')
def index():
    return 'Hello, world!'

if __name__ == '__main__':
    # Desative o reloader para evitar que o agendador seja iniciado mais de uma vez
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
