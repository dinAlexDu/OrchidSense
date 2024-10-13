import logging
import os
import random
import string
from mysql.connector import Error
from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

import atexit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest


# Local imports for tasks, database models, and sensor data operations
from tasks import check_and_send_alerts  # Task to check and send alerts
from models import db, User, UserConfig, Orquidea  # Database models
from orquideas_database import obter_dados_orquideas  # Orchid-related database operations (orquideas_database.py)
from orquideas_database import get_configs_alertas  # Orchid-related database operations (orquideas_database.py)
from users_database import conectar, obter_dados_utilizadores, obter_utilizador_por_email, obter_utilizador_por_id  # User database operations
import sensor_database as sensor_db  # Sensor database operations
from extensions import db, mail  # Extensions (SQLAlchemy, Mail)

# Upload folder configuration
UPLOAD_FOLDER = 'static/assets/img/illustrations/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Flask app initialization
app = Flask(__name__)

# Set the folder for profile image uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])  # Create the folder if it does not exist

# Check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Logger configuration
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# SQLAlchemy configuration for the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://pma:NtxFL6ms7pn3zRK2G9feDy@localhost/orchidsense_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration for sending emails
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dinis.duarte.istec@outlook.com'
app.config['MAIL_PASSWORD'] = 'zPnQ2CJmw4jNt9HausML8k'
app.config['MAIL_DEFAULT_SENDER'] = 'dinis.duarte.istec@outlook.com'

# Secret key for session management and CSRF protection
app.secret_key = 'TQZzvd37RV5ySfeGwjrU98'

# Initialize SQLAlchemy and Mail extensions
db.init_app(app)
mail = Mail(app)

# Flask-Login manager setup for handling user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to 'login' page if not authenticated

# Importing models after Flask initialization
from models import User, UserConfig, Orquidea

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the database by user ID.

    :param user_id: ID of the user to be loaded
    :return: User object or None if not found
    """
    utilizador = obter_utilizador_por_id(user_id)
    if utilizador:
        utilizador_id, utilizador_email, utilizador_password_hash, first_name, last_name, profile_image, is_admin = utilizador
        return User(
            id=utilizador_id,
            email=utilizador_email,
            password_hash=utilizador_password_hash,
            first_name=first_name,
            last_name=last_name,
            profile_image=profile_image,
            is_admin=is_admin
        )
    return None

# Global variables for sensor data
temperatura_atual = 0.0  # Current temperature value
humidade_atual = 0.0  # Current humidity value
luminosidade_atual = 0  # Current light intensity (lux)
ultima_insercao_lux = None  # Last time lux data was inserted
ultima_insercao_temp_hum = None  # Last time temperature and humidity data were inserted

dados_historicos = []  # Historical data for temperature and humidity
dados_historicos_lux = []  # Historical data for luminosity

# Function to start the background scheduler for alerts
def start_scheduler():
    """
    Starts a background scheduler that checks and sends alerts every 60 minutes.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_alerts, 'interval', minutes=60, args=[app])  # Schedule every 60 minutes
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False)) # Ensure shutdown on app exit
    app.logger.info("apscheduler iniciado e tarefa agendada para cada 60 minutos.")


start_scheduler()  # Start the scheduler when the app initializes

# Function to retrieve a user from the database by email
def obter_utilizador_por_email(email):
    """
        Retrieves a user from the database based on their email.

        :param email: The email of the user to retrieve
        :return: A user record or None if not found
        """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, password_hash, first_name, last_name, profile_image, is_admin FROM users WHERE email = %s', (email,))
    utilizador = cursor.fetchone()
    conn.close()
    return utilizador

# Route for the home page

@app.route('/')
def index():
    """
        Route for the home page.
        Redirects to the login page if the user is not authenticated, otherwise to the dashboard.

        :return: Redirect to the login page or dashboard
        """
    app.logger.debug('Acesso Página Index')
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Route for user login

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Route for user login.
        Validates the email and password. If successful, logs the user in and redirects to the dashboard.

        :return: Redirect to the dashboard on successful login, otherwise return login page with errors
        """
    if request.method == 'POST':
        email = request.form['inputEmailAddress']
        password = request.form['inputPassword']

        # Retrieve user from the database by email
        utilizador = obter_utilizador_por_email(email)

        if utilizador:
            utilizador_id, utilizador_email, utilizador_password_hash, first_name, last_name, profile_image, is_admin = utilizador
            # Verify password using check_password_hash
            if check_password_hash(utilizador_password_hash, password):
                user = User(id=utilizador_id, email=utilizador_email, password_hash=utilizador_password_hash,
                            is_admin=is_admin, profile_image=profile_image)
                login_user(user)

                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Palavra-passe incorrecta! Tente novamente.', 'danger')
        else:
            flash('E-mail não encontrado! verifique e tente novamente.', 'danger')

    return render_template('login.html')

# Route for logging out the user
@app.route('/logout')
@login_required
def logout():
    """
    Route to log out the current user.

    :return: Redirect to the login page after logging out
    """
    logout_user()
    return redirect(url_for('login'))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route to handle user registration.
    If a POST request is received, checks for email duplication, validates passwords, and creates a new user.

    :return: Redirect to the login page on success, or re-render the registration form with error messages.
    """
    if request.method == 'POST':
        email = request.form['inputEmailAddress']
        password = request.form['inputPassword']
        confirm_password = request.form['inputConfirmPassword']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        profile_image = request.form['profile_image']

        # Check if the email is already registered
        user = User.query.filter_by(email=email).first()
        if user:
            flash('E-Mail já registado')
            return redirect(url_for('register'))

        # Validate that the passwords match
        if password != confirm_password:
            flash('Passwords nao condizem')
            return redirect(url_for('register'))

        # Create a new user and add them to the database
        new_user = User(email=email, first_name=first_name, last_name=last_name, profile_image=profile_image)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Parabéns, conta criada!')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Placeholder for the password reset route.
    """
    pass


@app.route('/dashboard')
@login_required
def dashboard():
    """
    Route to display the dashboard with sensor data.
    Queries the database for temperature, humidity, and light data from the last 24 hours and displays graphs.

    :return: Rendered template of the dashboard with the latest sensor data.
    """
    app.logger.debug(f"User: {current_user.first_name} {current_user.last_name} - {current_user.email}")
    app.logger.debug('Página de dashboard acedida por {current_user.email}')

    # Query the sensor data for temperature and humidity from the last 24 hours

    dados_graficos = sensor_db.query_dados_sensor_temp_hum_ultimas_24_horas()
    dados_luminosidade = sensor_db.query_dados_sensor_luminosidade_ultimas_24_horas()

    if dados_graficos:
        # Sort the data by timestamp
        dados_graficos.sort(key=lambda x: x[0])  # A primeira coluna é data_hora
        labels = [registo[0].strftime('%H:%M') for registo in dados_graficos]
        temperaturas_grafico = [registo[1] for registo in dados_graficos]
        humidades_grafico = [registo[2] for registo in dados_graficos]
        temperatura_atual = temperaturas_grafico[-1] if temperaturas_grafico else 0
        humidade_atual = humidades_grafico[-1] if humidades_grafico else 0
    else:
        labels = []
        temperaturas_grafico = []
        humidades_grafico = []

    if dados_luminosidade:
        # Sort the data by timestamp
        dados_luminosidade.sort(key=lambda x: x[0])
        luminosidades_grafico = [registo[1] for registo in dados_luminosidade]
        luminosidade_atual = luminosidades_grafico[-1] if luminosidades_grafico else 0
    else:
        luminosidades_grafico = []

    app.logger.debug(f"Dados Graficos: {dados_graficos}")
    app.logger.debug(f"Dados Luminosidade: {dados_luminosidade}")

    return render_template('dashboard.html',
                           temperatura_atual=temperatura_atual,
                           humidade_atual=humidade_atual,
                           luminosidade_atual=luminosidade_atual,
                           labels=labels,
                           temperaturas=temperaturas_grafico,
                           humidades=humidades_grafico,
                           luminosidades=luminosidades_grafico)


@app.route('/biblioteca-orquideas')
@login_required
def biblioteca_orquideas():
    """
    Route to display the orchid library.
    Queries the database for orchid data and renders it in a template.

    :return: Rendered template of the orchid library with the queried data.
    """
    app.logger.debug('Página Biblioteca de Orquídeas acedida por {current_user.email}')

    dados_orquideas = obter_dados_orquideas()

    return render_template('biblioteca-orquideas.html', orquideas=dados_orquideas)


@app.route('/relatorios', methods=['GET', 'POST'])
@login_required
def relatorios():
    """
    Route to display reports.
    Queries the database for summarized sensor data and displays it in tables and graphs.

    :return: Rendered template of the reports page with the queried data.
    """
    dados_resumo_horario = sensor_db.relatorios_tabela_resumo_horario()
    dados_resumo_diario = sensor_db.relatorios_tabela_resumo_diario()
    dados_resumo_semanal = sensor_db.relatorios_tabela_resumo_semanal()
    dados_resumo_mensal = sensor_db.relatorios_tabela_resumo_mensal()
    dados_resumo_anual = sensor_db.relatorios_tabela_resumo_anual()

    return render_template('relatorios.html', dados_resumo_horario=dados_resumo_horario,
                           dados_resumo_diario=dados_resumo_diario, dados_resumo_semanal=dados_resumo_semanal,
                           dados_resumo_mensal=dados_resumo_mensal, dados_resumo_anual=dados_resumo_anual)


@app.route('/api/sensor_data', methods=['POST'])
def sensor_data_api():
    """
    API endpoint to receive and process temperature and humidity data from the DHT22 sensor.
    The data is stored in the database and returned as a JSON response.

    :return: JSON message indicating success or error.
    """
    global temperatura_atual, humidade_atual, dados_historicos
    global ultima_insercao_temp_hum

    try:
        data = request.get_json()

        app.logger.debug('Dados do sensor DHT22 recebidos (rota /api/sensor_data: %s)', data)

        temperatura_atual = data['temperatura']
        humidade_atual = data['humidade']

        data_atual = datetime.now()

        # Store the sensor data in the historical list
        dados_historicos.append({
            'data': data_atual,
            'temperatura': temperatura_atual,
            'humidade': humidade_atual
        })

        # Insert the data into the database if 15 minutes have passed since the last insertion

        if ultima_insercao_temp_hum is None or (data_atual - ultima_insercao_temp_hum).total_seconds() >= 900:  # 15 min
            sensor_db.inserir_dados_temp_hum(data['data_hora'], data['temperatura'], data['humidade'])
            ultima_insercao_temp_hum = data_atual
            app.logger.debug('Dados Hum & Temp inseridos na BD (rota /api/sensor_data)')

        return jsonify({'message': 'requisicao POST /api/sensor_data OK'}), 200
    except Exception as e:
        app.logger.error('Erro ao processar dados na rota /api/sensor_data: %s', e, exc_info=True)
        return jsonify({'error': 'Erro ao processar dados'}), 500


@app.route('/api/sensor_lux_data', methods=['POST'])
def sensor_lux_data_api():
    """
    API endpoint to receive and process light intensity data from the BH1750 sensor.
    The data is stored in the database and returned as a JSON response.

    :return: JSON message indicating success or error.
    """
    global luminosidade_atual
    global ultima_insercao_lux

    try:
        data = request.get_json()
        app.logger.debug('Dados do sensor BH17150 recebidos (rota /api/sensor_lux_data: %s)', data)

        luminosidade_atual = data['luminosidade']

        data_atual = datetime.now()

        # Store the light intensity data in the historical list

        dados_historicos_lux.append({
            'data': data_atual,
            'luminosidade': luminosidade_atual
        })

        # Insert the data into the database if 15 minutes have passed since the last insertion

        if ultima_insercao_lux is None or (data_atual - ultima_insercao_lux).total_seconds() >= 900:
            sensor_db.inserir_dados_luminosidade(data['data_hora'], data['luminosidade'])
            ultima_insercao_lux = data_atual
            app.logger.debug('Dados de luz inseridos na BD rota /api/sensor_lux_data')

        return jsonify({
                           'message': 'requisicao POST /api/sensor_lux_data OK'}), 200
    except Exception as e:
        app.logger.error('Erro ao processar dados na rota /api/sensor_lux_data: %s', e, exc_info=True)
        return jsonify({'error': 'Erro ao processar dados'}), 500


@app.route('/api/tempo_real')
@login_required
def dados_tempo_real():
    """
    API endpoint to return the real-time sensor data (temperature, humidity, and light intensity).

    :return: JSON object containing the real-time sensor data.
    """
    global temperatura_atual, humidade_atual, luminosidade_atual
    data = {
        'temperatura': temperatura_atual,
        'humidade': humidade_atual,
        'luminosidade': luminosidade_atual
    }
    app.logger.debug(f"Retorno de dados em tempo real rota /api/tempo_real: {data}")
    return jsonify(data)


@app.route('/notificacoes')
@login_required
def notificacoes():
    """
    Route to display user notifications.
    Retrieves the user's alert configurations and orchid data from the database.

    :return: Rendered template of the notifications page.
    """
    user_id = current_user.id

    configuracoes_alertas = get_configs_alertas(user_id)

    orquideas = Orquidea.query.all()

    return render_template('notificacoes.html', configuracoes_alertas=configuracoes_alertas, orquideas=orquideas)


@app.route('/get-orquideas', methods=['GET'])
@login_required
def get_orquideas():
    """
    API endpoint to retrieve orchid data.
    Queries the database for all orchids and returns the data as a JSON response.

    :return: JSON list of orchids.
    """
    orquideas = Orquidea.query.all()
    orquideas_list = [{'id': orquidea.id, 'nome': orquidea.nome} for orquidea in orquideas]
    return jsonify(orquideas_list), 200


@app.route('/add-config-alerta', methods=['POST'])
@login_required
def add_config_alerta():
    """
    API endpoint to add a new alert configuration for the user.
    Takes the user's orchid and sensor preferences and saves them to the database.

    :return: JSON response indicating success or failure.
    """
    data = request.get_json()
    user_id = current_user.id
    orquidea_id = data['orquidea']
    temp_min = float(data['temp_min'])
    temp_max = float(data['temp_max'])
    humidade_min = float(data['humidade_min'])
    humidade_max = float(data['humidade_max'])
    lux_min = int(data.get('lux_min', 0))
    lux_max = int(data.get('lux_max', 0))

    nova_configuracao = UserConfig(
        user_id=user_id,
        orquidea_id=orquidea_id,
        temp_min=temp_min,
        temp_max=temp_max,
        humidade_min=humidade_min,
        humidade_max=humidade_max,
        lux_min=lux_min,
        lux_max=lux_max
    )

    db.session.add(nova_configuracao)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Nova configuração adicionada com sucesso!'}), 200


@app.route('/edit-config-alerta/<int:id>', methods=['POST'])
@login_required
def edit_config_alerta(id):
    """
    API endpoint to edit an existing alert configuration.
    Takes the updated preferences from the user and updates the database.

    :param id: ID of the configuration to edit.
    :return: JSON response indicating success or failure.
    """
    data = request.get_json()

    configuracao = UserConfig.query.get(id)

    if configuracao:
        try:
            configuracao.temp_min = float(data['temp_min'])
            configuracao.temp_max = float(data['temp_max'])
            configuracao.humidade_min = float(data['humidade_min'])
            configuracao.humidade_max = float(data['humidade_max'])
            configuracao.lux_min = int(data.get('lux_min', 0))
            configuracao.lux_max = int(data.get('lux_max', 0))

            db.session.commit()

            return jsonify({'success': True, 'message': 'Configuração atualizada com sucesso!'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    else:
        return jsonify({'success': False, 'message': 'Configuração não encontrada!'}), 404


@app.route('/delete-config-alerta/<int:id>', methods=['DELETE'])
@login_required
def delete_config_alerta(id):
    """
    API endpoint to delete an existing alert configuration.
    Removes the configuration from the database.

    :param id: ID of the configuration to delete.
    :return: JSON response indicating success or failure.
    """
    configuracao = UserConfig.query.get(id)

    if configuracao:
        db.session.delete(configuracao)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Configuração excluída com sucesso!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Configuração não encontrada!'}), 404


@app.route('/gestao-dispositivos')
@login_required
def gestao_dispositivos():
    """
    Route to display device and sensor information.
    Provides details about the Raspberry Pi and the connected sensors (DHT22, BH1750).

    :return: Rendered template of the device management page.
    """
    dispositivo = {
        'nome': 'Raspberry Pi 3',
        'modelo': 'Model B Rev 1.2',
        'cpu': 'ARMv7 Processor rev 4 (v7l) 1.2 GHz quad-core ARM Cortex-A53',
        'ram': '921 MiB',
        'storage': 'MicroSD',
        'network': 'Ethernet (MAC: b8:27:eb:25:ea:e1), Wi-Fi (IP: 192.168.137.32, MAC: b8:27:eb:70:bf:b4)',
        'os': 'Raspbian GNU/Linux 11 (bullseye)'
    }

    sensor_dht22 = {
        'nome': 'DHT22',
        'intervalo_temperatura': '-40 a 80 °C',
        'intervalo_humidade': '0 a 100% RH',
        'precisao_temperatura': '±0.5 °C',
        'precisao_humidade': '±2-5% RH',
        'alimentacao': '3.3-6V DC',
        'consumo': 'Medição 1-1.5 mA, Stand-by 40-50 μA',
        'periodo_colecta': '> 2s',
        'transmissao': 'Distância de transmissão até 20 metros',
        'dimensoes': '15.1 x 25 x 7.7 mm'
    }

    sensor_bh1750 = {
        'nome': 'BH1750',
        'intervalo_medicao': '1 a 65535 lux',
        'precisao': '±20%',
        'alimentacao': '3.3-5V DC',
        'corrente_sda': '7 mA',
        'dissipacao_potencia': '260 mW',
        'dimensoes': '20 x 30 mm'
    }

    return render_template('gestao-dispositivos.html', dispositivo=dispositivo, sensor_dht22=sensor_dht22,
                           sensor_bh1750=sensor_bh1750)


@app.route('/gestao-utilizadores')
@login_required
def gestao_utilizadores():
    """
    Route for user management.
    Only accessible to admins. Lists all users in the system.

    :return: Rendered template of the user management page.
    """
    app.logger.debug('Página Gestão de Utilizadores acedida por {current_user.email}')

    # Verificar user admin
    if not current_user.is_admin:
        app.logger.debug('Utilizador não autorizado tentou aceder a página de Gestão de Utilizadores')
        return redirect(url_for('index'))  # Redireciona para index

    dados_utilizadores = obter_dados_utilizadores()
    return render_template('gestao-utilizadores.html', users=dados_utilizadores)


@app.route('/gestao-utilizadores-add-user', methods=['GET', 'POST'])
@login_required
def gestao_utilizadores_add_user():
    """
    Route to add a new user in the system.
    Only accessible to admins. Sends an email with a temporary password to the newly created user.

    :return: Rendered template of the add user page or redirect to user management on success.
    """
    if not current_user.is_admin:
        return redirect(url_for('index'))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        role = request.form.get('role')

        if not first_name or not last_name or not email or not role:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('gestao_utilizadores_add_user'))

        is_admin = role == 'administrator'

        file = request.files.get('profile_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_image = filename
        else:
            profile_image = 'profile-1.png'

        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        password_hash = generate_password_hash(temp_password)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            profile_image=profile_image,
            is_admin=is_admin
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            msg = Message('Orchidsense - nova conta', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
            msg.body = f'Olá {first_name},\n\nA sua conta OrchiSense está activa. Use a palavra-passe abaixo para entrar.\n\nPalavra-Passe: {temp_password}\n\nCumprimentos,\nOrchidSense'
            mail.send(msg)

            flash('Utilizador adicionado com sucesso! E-mail enviado.')
            return redirect(url_for('gestao_utilizadores'))
        except Error as e:
            db.session.rollback()
            if e.errno == 1062:
                flash('Erro: O email já está em uso. Por favor, use um email diferente.', 'error')
                return redirect(url_for('gestao_utilizadores_add_user'))
            else:
                flash(f"Erro ao adicionar utilizador: {e}", 'error')
                return render_template('error-500.html')

    return render_template('gestao-utilizadores-add-user.html')



@app.route('/editar-utilizador/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_utilizador(user_id):
    """
    Route to edit user details.
    Only accessible to admins. Allows modification of the user's information.

    :param user_id: The ID of the user to edit.
    :return: Rendered template of the edit user page or redirect to user management on success.
    """
    if not current_user.is_admin:
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.is_admin = request.form.get('is_admin') == '1'

        # Handle profile image upload
        file = request.files.get('profile_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_image = filename

        db.session.commit()
        return redirect(url_for('gestao_utilizadores'))

    return render_template('gestao-utilizadores-edit-user.html', user=user)



@app.route('/excluir-utilizador/<int:user_id>', methods=['POST'])
@login_required
def excluir_utilizador(user_id):
    """
    Route to delete a user.
    Only accessible to admins. Removes the user from the database.

    :param user_id: The ID of the user to delete.
    :return: Redirect to user management after deletion.
    """
    if not current_user.is_admin:
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('gestao_utilizadores'))


@app.route('/api/get-historic-data')
@login_required
def get_historic_data():
    """
    API endpoint to retrieve historic sensor data.
    Queries the database for all recorded sensor data and returns it as a JSON response.

    :return: JSON list of sensor data.
    """
    registos = sensor_db.recuperar_dados_sensor()
    try:
        registros = sensor_db.recuperar_dados_sensor()
        dados = [{
            'id': registro[0],
            'data_hora': registro[1].strftime("%Y-%m-%d %H:%M:%S"),
            'temperatura': registro[2],
            'humidade': registro[3]
        } for registro in registros]
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/dados/horario')
@login_required
def dados_horario():
    """
    API endpoint to retrieve hourly sensor data summaries.
    Queries the database for sensor data grouped by hour and returns the results as JSON.

    :return: JSON object with hourly data for temperature, humidity, and luminosity.
    """
    dados_graficos = sensor_db.relatorios_grafico_resumo_horario()
    labels = [f'{resultado[1]}h' for resultado in dados_graficos]
    temp_maximas = [resultado[2] for resultado in dados_graficos]
    temp_minimas = [resultado[3] for resultado in dados_graficos]
    temp_medias = [resultado[4] for resultado in dados_graficos]
    hum_maximas = [resultado[5] for resultado in dados_graficos]
    hum_minimas = [resultado[6] for resultado in dados_graficos]
    hum_medias = [resultado[7] for resultado in dados_graficos]
    lux_maximas = [resultado[8] for resultado in dados_graficos]
    lux_minimas = [resultado[9] for resultado in dados_graficos]
    lux_medias = [resultado[10] for resultado in dados_graficos]

    return jsonify({
        'labels': labels,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias,
        'lux_maximas': lux_maximas,
        'lux_minimas': lux_minimas,
        'lux_medias': lux_medias
    })


@app.route('/api/dados/diario')
@login_required
def dados_diario():
    """
    API endpoint to retrieve daily sensor data summaries.
    Queries the database for sensor data grouped by day and returns the results as JSON.

    :return: JSON object with daily data for temperature, humidity, and luminosity.
    """
    dados_graficos = sensor_db.relatorios_grafico_resumo_diario()
    labels_diario = [resultado[0].strftime('%Y-%m-%d') for resultado in dados_graficos]
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]
    lux_maximas = [resultado[7] for resultado in dados_graficos]
    lux_minimas = [resultado[8] for resultado in dados_graficos]
    lux_medias = [resultado[9] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_diario,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias,
        'lux_maximas': lux_maximas,
        'lux_minimas': lux_minimas,
        'lux_medias': lux_medias
    })


@app.route('/api/dados/semanal')
@login_required
def dados_semanal():
    """
    API endpoint to retrieve weekly sensor data summaries.
    Queries the database for sensor data grouped by week and returns the results as JSON.

    :return: JSON object with weekly data for temperature, humidity, and luminosity.
    """
    dados_graficos = sensor_db.relatorios_grafico_resumo_semanal()
    labels_semanal = [f'Semana {resultado[0]}' for resultado in dados_graficos]
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]
    lux_maximas = [resultado[7] for resultado in dados_graficos]
    lux_minimas = [resultado[8] for resultado in dados_graficos]
    lux_medias = [resultado[9] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_semanal,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias,
        'lux_maximas': lux_maximas,
        'lux_minimas': lux_minimas,
        'lux_medias': lux_medias
    })


@app.route('/api/dados/mensal')
def dados_mensal():
    """
    API endpoint to retrieve monthly sensor data summaries.
    Queries the database for sensor data grouped by month and returns the results as JSON.

    :return: JSON object with monthly data for temperature, humidity, and luminosity.
    """
    dados_graficos = sensor_db.relatorios_grafico_resumo_mensal()
    labels_mensal = [f'Mês {resultado[0]}' for resultado in dados_graficos]
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]
    lux_maximas = [resultado[7] for resultado in dados_graficos]
    lux_minimas = [resultado[8] for resultado in dados_graficos]
    lux_medias = [resultado[9] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_mensal,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias,
        'lux_maximas': lux_maximas,
        'lux_minimas': lux_minimas,
        'lux_medias': lux_medias
    })


@app.route('/api/dados/anual')
def dados_anual():
    """
    API endpoint to retrieve yearly sensor data summaries.
    Queries the database for sensor data grouped by year and returns the results as JSON.

    :return: JSON object with yearly data for temperature, humidity, and luminosity.
    """
    dados_graficos = sensor_db.relatorios_grafico_resumo_anual()
    labels_anual = [f'Ano {resultado[0]}' for resultado in dados_graficos]
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]
    lux_maximas = [resultado[7] for resultado in dados_graficos]
    lux_minimas = [resultado[8] for resultado in dados_graficos]
    lux_medias = [resultado[9] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_anual,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias,
        'lux_maximas': lux_maximas,
        'lux_minimas': lux_minimas,
        'lux_medias': lux_medias
    })


@app.route('/export/excel')
@login_required
def export_excel():
    """
    Route to export sensor data as an Excel file.
    Generates a simple Excel file with data and sends it as an attachment for download.

    :return: Excel file download.
    """
    dados = {
        'Coluna1': [1, 2, 3, 4, 5],
        'Coluna2': ['A', 'B', 'C', 'D', 'E']
    }

    df = pd.DataFrame(dados)

    filename = 'dados.xlsx'
    df.to_excel(filename, index=False)

    return send_file(filename, as_attachment=True)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """
    Custom handler for 404 errors (page not found).
    Renders a custom 404 error page.

    :return: Rendered 404 error template.
    """
    return render_template('error-404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error-500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('error-403.html'), 403

# Test routes for debugging and testing email functionality
@app.route('/test_email')
def test_email():
    """
    Route to send a test email.
    Sends a simple test email to the specified address.

    :return: Success or error message.
    """
    try:
        msg = Message("Teste de E-mail", recipients=["dinis.duarte@my.istec.pt"])
        msg.body = "E-mail de teste."
        mail.send(msg)
        return "E-mail enviado com sucesso!"
    except Exception as e:
        app.logger.error(f"Erro ao enviar e-mail de teste: {e}")
        return str(e)


@app.route('/test_users')
def test_users():
    """
    Route to test user query with notifications enabled.
    Queries the database for users who have notifications enabled and lists their emails.

    :return: List of user emails with active notifications.
    """
    with app.app_context():
        users = User.query.filter_by(notifications_enabled=True).all()
        user_emails = [user.email for user in users]
        return f"Users com notificações activas: {user_emails}"


@app.route('/test-alert-email')
def test_alert_email():
    """
    Route to test sending alert emails.
    Sends a test alert email based on dummy configuration and data.

    :return: Success or error message.
    """
    try:
        fake_user_email = "dinis.duarte@my.istec.pt"
        fake_config = {
            'temp_min': 15,
            'temp_max': 25,
            'humidade_min': 30,
            'humidade_max': 70
        }
        fake_data = {
            'temperature': 26,
            'humidity': 80
        }
        send_alert_email(fake_user_email, fake_config, fake_data)
        return 'E-mail de alerta enviado com sucesso!'
    except Exception as e:
        return f'Erro ao enviar e-mail de alerta: {str(e)}'


@app.route('/test-alerts')
def test_alerts():
    """
    Route to trigger manual alert checks.
    Runs the alert checking routine manually to test alert functionality.

    :return: Success or error message.
    """
    try:
        check_and_send_alerts()
        return 'Alertas verificados com sucesso!'
    except Exception as e:
        return str(e), 500


def enviar_email(destinatario, assunto, corpo):
    """
    Sends an email with the specified recipient, subject, and body content.

    :param destinatario: Email recipient.
    :param assunto: Email subject.
    :param corpo: Email body content.
    """
    msg = Message(assunto, sender='dinis.duarte.istec@outlook.com', recipients=[destinatario])
    msg.body = corpo
    mail.send(msg)

# Main entry point for the Flask app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Retrieve the most recent lux and temp/humidity records
        ultima_insercao_lux = sensor_db.ultimo_registo_lux()
        if ultima_insercao_lux is None:
            ultima_insercao_lux = datetime.now()
        ultima_insercao_temp_hum = sensor_db.ultimo_registo_temp_hum()
        if ultima_insercao_temp_hum is None:
            ultima_insercao_temp_hum = datetime.now()
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
