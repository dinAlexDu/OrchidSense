import logging
from flask import current_app as app
from flask_mail import Message
from models import db, UserConfig, User, Orquidea
from extensions import db, mail
from tabulate import tabulate
from models import UserConfig, Orquidea
from sensor_database import get_latest_sensor_data
from sensor_database import get_sensor_data_last_hour

def check_and_send_alerts(app):
    with app.app_context():
        app.logger.debug("check_and_send_alerts - A iniciar a verificação de alertas...")
        user_configs = UserConfig.query.all()
        temp_hum_data, lux_data = get_sensor_data_last_hour()

        if not temp_hum_data or not lux_data:
            app.logger.info("check_and_send_alerts - Nenhum dado encontrado na BD.")
            return

        for config in user_configs:
            alerta_enviado = False  # Flag para evitar envio de múltiplos e-mails para o mesmo usuário
            for temp_hum_record in temp_hum_data:
                if alerta_enviado:
                    break  # Se já enviou um e-mail para este usuário, sai do loop

                for lux_record in lux_data:
                    temp_hum_time = temp_hum_record['data_hora']
                    lux_time = lux_record['data_hora']
                    time_diff = abs((temp_hum_time - lux_time).total_seconds())

                    # Considerando um intervalo de 60 segundos para coincidência dos dados
                    if time_diff <= 60:
                        if (temp_hum_record['temperatura'] < config.temp_min or temp_hum_record['temperatura'] > config.temp_max) or \
                           (temp_hum_record['humidade'] < config.humidade_min or temp_hum_record['humidade'] > config.humidade_max) or \
                           (lux_record['luminosidade'] < config.lux_min or lux_record['luminosidade'] > config.lux_max):
                            app.logger.debug(f"Condições ultrapassadas para o utilizador {config.user_id}. A enviar e-mail para {config.user.email}...")
                            send_alert_email(app, config.user.email, config, {
                                'temperatura': temp_hum_record['temperatura'],
                                'humidade': temp_hum_record['humidade'],
                                'luminosidade': lux_record['luminosidade'],
                                'data_hora': temp_hum_record['data_hora']
                            })
                            alerta_enviado = True
                            break  # Não precisa verificar mais registros para este usuário após encontrar uma condição ultrapassada
                        else:
                            app.logger.debug(f"Condições dentro dos limites para o utilizador {config.user_id}.")


def send_alert_email(app, email, config, data):
    with app.app_context():
        try:
            orquidea_nome = Orquidea.query.get(config.orquidea_id).nome
            msg = Message(
                'OrchidSense - Alerta de condições ambientais',
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            msg.body = f"""
            Olá,

            As condições ambientais para a orquídea {orquidea_nome} estão fora dos limites configurados:

            ----------------------------------------------------------------
            |               Detalhes das Condições Ambientais                          |
            ------------------------------------------------------------------------------------
            | Indicador     | Valor Actual | Intervalo Configurado (min.-máx.) |
            ----------------------------------------------------------------
            | Temperatura   | {data['temperatura']} °C      | {config.temp_min} - {config.temp_max} °C       |
            ----------------------------------------------------------------
            | Humidade      | {data['humidade']} %         | {config.humidade_min} - {config.humidade_max} % |
            ----------------------------------------------------------------
            | Luminosidade  | {data['luminosidade']} lux    | {config.lux_min} - {config.lux_max} lux      |
            ----------------------------------------------------------------

            Por favor, tome as medidas necessárias por forma a garantir que as condições ambientais da sua orquídea estejam dentro dos limites desejados.

            Atenciosamente,
            OrchidSense
            """
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Erro ao enviar e-mail: {str(e)}")

