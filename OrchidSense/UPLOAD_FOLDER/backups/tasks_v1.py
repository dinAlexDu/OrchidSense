import logging
from flask_mail import Message

from flask import current_app as app
from flask_mail import Message
from models import db, UserConfig, User, Orquidea
from extensions import db, mail
from models import UserConfig, Orquidea
from sensor_database import get_latest_sensor_data

def check_and_send_alerts(app):
    with app.app_context():
        app.logger.debug("A iniciar a verificação de alertas...")
        user_configs = UserConfig.query.all()
        for config in user_configs:
            latest_data = get_latest_sensor_data()
            if not latest_data:
                app.logger.info("Nenhum dado de sensor encontrado.")
                continue

            app.logger.debug(f"Dados do sensor recebidos: {latest_data}")
            if (latest_data['temperatura'] < config.temp_min or latest_data['temperatura'] > config.temp_max) or \
               (latest_data['humidade'] < config.humidade_min or latest_data['humidade'] > config.humidade_max):
                app.logger.debug(f"Condições ultrapassadas para o utilizador {config.user_id}. A enviar e-mail...")
                send_alert_email(app, config.user.email, config, latest_data)
            else:
                app.logger.debug(f"Condições dentro dos limites para o utilizador {config.user_id}.")

def send_alert_email(app, email, config, data):
    with app.app_context():
        try:
            orquidea_nome = Orquidea.query.get(config.orquidea_id).nome
            msg = Message(
                'Alerta de condições de temperatura e humidade',
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            msg.body = f"""
            Temperatura e/ou Humidade ultrapassadas para {orquidea_nome}:
            
            Temperatura actual: {data['temperatura']} (Intervalo de Temperatura min.-máx. tolerada: {config.temp_min}-{config.temp_max})
            Humidade actual: {data['humidade']} (Intervalo de Humidade min.-máx. tolerada: {config.humidade_min}-{config.humidade_max})
            """
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Erro ao enviar e-mail: {str(e)}")

