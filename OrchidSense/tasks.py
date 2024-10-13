import logging
from flask import current_app as app
from flask_mail import Message
from models import db, UserConfig, User, Orquidea
from extensions import db, mail
from tabulate import tabulate
from models import UserConfig, Orquidea
from sensor_database import get_latest_sensor_data
from sensor_database import get_sensor_data_last_hour

# Function to check user-configured alert thresholds and send alert emails if necessary.
def check_and_send_alerts(app):
    with app.app_context():
        app.logger.debug("check_and_send_alerts - A iniciar a verificação de alertas...")

        # Fetch all user configurations for monitoring (temperature, humidity, light).
        user_configs = UserConfig.query.all()

        # Retrieve sensor data (temperature, humidity, and light) from the last hour.
        temp_hum_data, lux_data = get_sensor_data_last_hour()

        # If no sensor data is available, log the info and stop further checks.
        if not temp_hum_data or not lux_data:
            app.logger.info("check_and_send_alerts - Nenhum dado encontrado na BD.")
            return

        # Loop through each user configuration to check if alert conditions are met.
        for config in user_configs:
            alerta_enviado = False  # Flag to prevent sending multiple emails to the same user.
            for temp_hum_record in temp_hum_data:
                if alerta_enviado:
                    break  # If an alert email was already sent, skip further checks for this user.

                for lux_record in lux_data:
                    temp_hum_time = temp_hum_record['data_hora']  # Timestamp for temperature and humidity record.
                    lux_time = lux_record['data_hora']  # Timestamp for luminosity record.

                    # Calculate the time difference between the two records.
                    time_diff = abs((temp_hum_time - lux_time).total_seconds())

                    # If the time difference is less than or equal to 60 seconds, consider the data synchronized.
                    # Check if any environmental condition (temperature, humidity, light) is out of user-configured bounds.
                    if time_diff <= 60:
                        if (temp_hum_record['temperatura'] < config.temp_min or temp_hum_record['temperatura'] > config.temp_max) or \
                           (temp_hum_record['humidade'] < config.humidade_min or temp_hum_record['humidade'] > config.humidade_max) or \
                           (lux_record['luminosidade'] < config.lux_min or lux_record['luminosidade'] > config.lux_max):

                            # Log and send an alert email if conditions are exceeded.
                            app.logger.debug(f"Condições ultrapassadas para o utilizador {config.user_id}. A enviar e-mail para {config.user.email}...")
                            send_alert_email(app, config.user.email, config, {
                                'temperatura': temp_hum_record['temperatura'],
                                'humidade': temp_hum_record['humidade'],
                                'luminosidade': lux_record['luminosidade'],
                                'data_hora': temp_hum_record['data_hora']
                            })
                            alerta_enviado = True  # Set the flag to prevent additional emails for this user.
                            break  # Stop checking further records for this user once an alert is triggered.
                        else:
                            # Log if conditions are within bounds for this user.
                            app.logger.debug(f"Condições dentro dos limites para o utilizador {config.user_id}.")

# Function to send an alert email when environmental conditions exceed configured thresholds.
def send_alert_email(app, email, config, data):
    with app.app_context():
        try:
            # Get the name of the orchid associated with the user's configuration.
            orquidea_nome = Orquidea.query.get(config.orquidea_id).nome
            msg = Message(
                'OrchidSense - Alerta de condições ambientais',  # Subject
                sender=app.config['MAIL_DEFAULT_SENDER'],  # Sender's email (configured in Flask-Mail)
                recipients=[email]  # Recipient's email (user)
            )

            # Data for the alert table (current values and configured ranges).
            table_data = [
                ["Temperatura", f"{data['temperatura']} °C", f"{config.temp_min} - {config.temp_max} °C"],
                ["Humidade", f"{data['humidade']} %", f"{config.humidade_min} - {config.humidade_max} %"],
                ["Luminosidade", f"{data['luminosidade']} lux", f"{config.lux_min} - {config.lux_max} lux"]
            ]

            # Format the data into a readable table using the 'tabulate' library.
            table_str = tabulate(table_data, headers=["Indicador", "Valor Actual", "Intervalo Configurado (min.-máx.)"], tablefmt="simple")
            table_str = '\n' + table_str  # Add line break before the table.

            # Email body with alert details.
            msg.body = f"""
            
            Olá,

            As condições ambientais para a orquídea {orquidea_nome} estão fora dos limites configurados.
            

            {table_str}

            
            """
            # Send the email using Flask-Mail.
            mail.send(msg)

            # Handle any errors that occur during email sending and log the error.
        except Exception as e:
            app.logger.error(f"Erro ao enviar e-mail: {str(e)}")
