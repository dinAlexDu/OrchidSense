import logging
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

app = Flask(__name__)

scheduler = BackgroundScheduler()  # Move esta linha para o topo do arquivo

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.DEBUG)

def check_and_send_alerts():
    app.logger.debug("Verificação de alertas iniciada.")
    app.logger.debug("Alerta enviado para condição X.")
    app.logger.debug("Verificação de alertas concluída.")

# def start_scheduler():
#     app.logger.info("Iniciando o agendador...")
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(func=check_and_send_alerts, trigger=IntervalTrigger(seconds=10))
#     scheduler.start()
#     atexit.register(lambda: scheduler.shutdown(wait=False))
#     app.logger.info("Agendador iniciado e tarefa agendada para cada 10 segundos.")
def start_scheduler():
    global scheduler
    if not scheduler.running:
        app.logger.info("Iniciando o agendador...")
        scheduler.add_job(func=check_and_send_alerts, trigger='interval', minutes=1)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown(wait=False))
        app.logger.info("Agendador iniciado e tarefa agendada para cada 5 minutos.")
    else:
        app.logger.info("O agendador já está rodando.")




@app.route('/start-scheduler')
def start_scheduler_route():
    start_scheduler()
    return "Agendador iniciado!"

# @app.route('/start-scheduler')
# def start_scheduler_route():
#     if not scheduler.running:
#         start_scheduler()
#         return "Agendador iniciado!"
#     else:
#         return "Agendador já está rodando."


@app.route('/')
def index():
    return 'Hello, world!'

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    start_scheduler()  # Inicia o agendador antes de iniciar o servidor
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)