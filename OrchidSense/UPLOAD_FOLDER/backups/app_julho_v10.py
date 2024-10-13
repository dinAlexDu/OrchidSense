import logging
from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

import atexit
from werkzeug.security import generate_password_hash, check_password_hash

#local
from tasks import check_and_send_alerts
from models import db, User, UserConfig, Orquidea
from orquideas_database import obter_dados_orquideas  # orquideas_database.py
from orquideas_database import get_configs_alertas  # orquideas_database.py
from users_database import obter_dados_utilizadores  #users_databse
import sensor_database as sensor_db
from extensions import db, mail

app = Flask(__name__)

# Logger
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://pma:NtxFL6ms7pn3zRK2G9feDy@localhost/orchidsense_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Flask-Mail
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dinis.duarte.istec@outlook.com'
app.config['MAIL_PASSWORD'] = 'zPnQ2CJmw4jNt9HausML8k'
app.config['MAIL_DEFAULT_SENDER'] = 'dinis.duarte.istec@outlook.com'
# Define a chave secreta
app.secret_key = 'TQZzvd37RV5ySfeGwjrU98'

# extensions
db.init_app(app)
mail = Mail(app)


# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# Importações apos init

from models import User, UserConfig, Orquidea

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# Variáveis globais
temperatura_atual = 0.0
humidade_atual = 0.0
luminosidade_atual = 0
ultima_insercao_lux = None
ultima_insercao_temp_hum = None



dados_historicos = []
dados_historicos_lux = []



def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_alerts, 'interval', minutes=60, args=[app]) # 60 mins
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
    app.logger.info("apscheduler iniciado e tarefa agendada para cada 60 minutos.")
start_scheduler()

@app.route('/')
def index():
    app.logger.debug('Acesso Página Index')
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form)
        email = request.form['inputEmailAddress']
        password = request.form['inputPassword']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['inputEmailAddress']
        password = request.form['inputPassword']
        confirm_password = request.form['inputConfirmPassword']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        profile_image = request.form['profile_image']


        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already registered')
            return redirect(url_for('register'))


        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))


        new_user = User(email=email, first_name=first_name, last_name=last_name, profile_image=profile_image)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    pass


@app.route('/dashboard')
@login_required
def dashboard():
    app.logger.debug('Página de dashboard acedida')

    dados_graficos = sensor_db.query_dados_sensor_temp_hum_ultimas_24_horas()
    dados_luminosidade = sensor_db.query_dados_sensor_luminosidade_ultimas_24_horas()


    if dados_graficos:
        # Ordenar por data_hora
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
        # Ordenar por data_hora
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
    app.logger.debug('Página da Biblioteca de Orquídeas acedida')

    dados_orquideas = obter_dados_orquideas()

    return render_template('biblioteca-orquideas.html', orquideas=dados_orquideas)


@app.route('/relatorios', methods=['GET', 'POST'])
@login_required
def relatorios():
    dados_resumo_horario = sensor_db.relatorios_tabela_resumo_horario()
    dados_resumo_diario = sensor_db.relatorios_tabela_resumo_diario()
    dados_resumo_semanal = sensor_db.relatorios_tabela_resumo_semanal()
    dados_resumo_mensal = sensor_db.relatorios_tabela_resumo_mensal()
    dados_resumo_anual = sensor_db.relatorios_tabela_resumo_anual()

    return render_template('relatorios.html', dados_resumo_horario=dados_resumo_horario, dados_resumo_diario=dados_resumo_diario, dados_resumo_semanal=dados_resumo_semanal, dados_resumo_mensal=dados_resumo_mensal, dados_resumo_anual=dados_resumo_anual)


@app.route('/api/sensor_data', methods=['POST'])
def sensor_data_api():
    global temperatura_atual, humidade_atual, dados_historicos
    global ultima_insercao_temp_hum

    try:
        data = request.get_json()

        app.logger.debug('Dados do sensor DHT22 recebidos (rota /api/sensor_data: %s)', data)

        temperatura_atual = data['temperatura']
        humidade_atual = data['humidade']

        data_atual = datetime.now()

        dados_historicos.append({
            'data': data_atual,
            'temperatura': temperatura_atual,
            'humidade': humidade_atual
        })

        if ultima_insercao_temp_hum is None or (data_atual - ultima_insercao_temp_hum).total_seconds() >= 900: # 15 min
            sensor_db.inserir_dados_temp_hum(data['data_hora'], data['temperatura'], data['humidade'])
            ultima_insercao_temp_hum = data_atual
            app.logger.debug('Dados Hum & Temp inseridos na BD (rota /api/sensor_data)')

        return jsonify({'message': 'requisicao POST /api/sensor_data com sucesso'}), 200
    except Exception as e:
        app.logger.error('Erro ao processar dados na rota /api/sensor_data: %s', e, exc_info=True)
        return jsonify({'error': 'Erro ao processar dados'}), 500

@app.route('/api/sensor_lux_data', methods=['POST'])
def sensor_lux_data_api():
    global luminosidade_atual
    global ultima_insercao_lux

    try:
        data = request.get_json()
        app.logger.debug('Dados do sensor BH17150 recebidos (rota /api/sensor_lux_data: %s)', data)

        luminosidade_atual = data['luminosidade']

        data_atual = datetime.now()

        dados_historicos_lux.append({
            'data': data_atual,
            'luminosidade': luminosidade_atual
        })

        if ultima_insercao_lux is None or (data_atual - ultima_insercao_lux).total_seconds() >= 900:
            sensor_db.inserir_dados_luminosidade(data['data_hora'], data['luminosidade'])
            ultima_insercao_lux = data_atual
            app.logger.debug('Dados de luz inseridos na BD rota /api/sensor_lux_data')

        return jsonify({'message': 'requisicao POST /api/sensor_lux_data sucesso e dados do sensor bh1750 recebidos corretamente'}), 200
    except Exception as e:
        app.logger.error('Erro ao processar dados na rota /api/sensor_lux_data: %s', e, exc_info=True)
        return jsonify({'error': 'Erro ao processar dados'}), 500

@app.route('/api/tempo_real')
@login_required
def dados_tempo_real():
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
    user_id = current_user.id

    configuracoes_alertas = get_configs_alertas(user_id)

    orquideas = Orquidea.query.all()

    return render_template('notificacoes.html', configuracoes_alertas=configuracoes_alertas, orquideas=orquideas)

@app.route('/get-orquideas', methods=['GET'])
@login_required
def get_orquideas():
    orquideas = Orquidea.query.all()
    orquideas_list = [{'id': orquidea.id, 'nome': orquidea.nome} for orquidea in orquideas]
    return jsonify(orquideas_list), 200


@app.route('/add-config-alerta', methods=['POST'])
@login_required
def add_config_alerta():
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

    return render_template('dispositivos.html', dispositivo=dispositivo, sensor_dht22=sensor_dht22,
                           sensor_bh1750=sensor_bh1750)

@app.route('/gestao-utilizadores')
@login_required
def gestao_utilizadores():
    app.logger.debug('Página de Gestão de Utilizadores acedida')

    dados_utilizadores = obter_dados_utilizadores()

    return render_template('gestao-utilizadores.html', users=dados_utilizadores)


@app.route('/api/get-historic-data')
@login_required
def get_historic_data():
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
    dados = {
        'Coluna1': [1, 2, 3, 4, 5],
        'Coluna2': ['A', 'B', 'C', 'D', 'E']
    }

    df = pd.DataFrame(dados)

    filename = 'dados.xlsx'
    df.to_excel(filename, index=False)

    return send_file(filename, as_attachment=True)

#TESTES
@app.route('/test_email')
def test_email():
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
    with app.app_context():
        users = User.query.filter_by(notifications_enabled=True).all()
        user_emails = [user.email for user in users]
        return f"Users com notificações activas: {user_emails}"



@app.route('/test-alert-email')
def test_alert_email():
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
    try:
        check_and_send_alerts()
        return 'Alertas verificados com sucesso!'
    except Exception as e:
        return str(e), 500

def enviar_email(destinatario, assunto, corpo):
    msg = Message(assunto, sender='dinis.duarte.istec@outlook.com', recipients=[destinatario])
    msg.body = corpo
    mail.send(msg)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ultima_insercao_lux = sensor_db.ultimo_registo_lux()
        if ultima_insercao_lux is None:
            ultima_insercao_lux = datetime.now()
        ultima_insercao_temp_hum = sensor_db.ultimo_registo_temp_hum()
        if ultima_insercao_temp_hum is None:
            ultima_insercao_temp_hum = datetime.now()
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)