import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta  # Importe a classe datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
#locais
from tasks import check_and_send_alerts
from models import db, User, UserConfig, Orquidea
from orquideas_database import obter_dados_orquideas  # Importa a função do arquivo database.py
import sensor_database as sensor_db
from extensions import db, mail

app = Flask(__name__)

# Configuração do Logger
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://pma:NtxFL6ms7pn3zRK2G9feDy@localhost/orchidsense_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dinis.duarte.istec@outlook.com'
app.config['MAIL_PASSWORD'] = 'zPnQ2CJmw4jNt9HausML8k'
app.config['MAIL_DEFAULT_SENDER'] = 'dinis.duarte.istec@outlook.com'  # Opcional, mas recomendado
# Define a chave secreta
app.secret_key = 'TQZzvd37RV5ySfeGwjrU98'  # Substitua 'sua_chave_secreta_aqui' por uma chave forte e única

# Inicializa extensões
db.init_app(app)
mail = Mail(app)


# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# Importações que podem causar circular import são feitas após inicializações

from models import User, UserConfig, Orquidea

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Use diretamente User



# Variáveis globais para armazenar os dados atuais do sensor
temperatura_atual = 0.0
humidade_atual = 0.0
luminosidade_atual = 0
ultima_insercao_lux = None
ultima_insercao_temp_hum = None


# Inicialize uma lista vazia para armazenar os dados históricos
dados_historicos = []
dados_historicos_lux = []



def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_alerts, 'interval', minutes=1, args=[app])
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
    app.logger.info("Agendador iniciado e tarefa agendada para cada 1 minutos.")
start_scheduler()

@app.route('/')
def index():
    app.logger.debug('Página inicial acessada')
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form)  # Ver o que está sendo recebido
        email = request.form['inputEmailAddress']
        password = request.form['inputPassword']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    app.logger.debug('Página de dashboard acessada')
    # Os dados em tempo real são mantidos conforme recebidos pelo simulate_sensor_data.py

    # Para os gráficos, usamos os dados armazenados na base de dados das últimas 24 horas
    dados_graficos = sensor_db.recuperar_dados_sensor_temp_hum_ultimas_24_horas()
    dados_luminosidade = sensor_db.recuperar_dados_luminosidade_ultimas_24_horas()  # Adicione uma função para recuperar esses dados

    labels = [registo[1].strftime('%H:%M') for registo in dados_graficos]
    temperaturas_grafico = [registo[2] for registo in dados_graficos]
    humidades_grafico = [registo[3] for registo in dados_graficos]
    luminosidades_grafico = [registo[2] for registo in dados_luminosidade]  # Supondo que o índice 2 seja de luminosidade

    # Assegure-se de que temperatura_atual, humidade_atual e luminosidade_atual estão definidas
    temperatura_atual = temperaturas_grafico[-1] if temperaturas_grafico else 0
    humidade_atual = humidades_grafico[-1] if humidades_grafico else 0
    luminosidade_atual = luminosidades_grafico[-1] if luminosidades_grafico else 0  # Garanta que este valor está sendo atualizado adequadamente

    # A função render_template passa tanto os dados em tempo real quanto os dados para os gráficos
    return render_template('dashboard.html',
                           temperatura_atual=temperatura_atual,
                           humidade_atual=humidade_atual,
                           luminosidade_atual=luminosidade_atual,
                           labels=labels,
                           temperaturas=temperaturas_grafico,
                           humidades=humidades_grafico,
                           luminosidades=luminosidades_grafico)




@app.route('/biblioteca-orquideas')
def biblioteca_orquideas():
    app.logger.debug('Página da Biblioteca de Orquídeas acedida')

    # Chamada à função para obter dados das orquídeas
    dados_orquideas = obter_dados_orquideas()

    # Renderizar o template com os dados das orquídeas
    return render_template('biblioteca-orquideas.html', orquideas=dados_orquideas)


@app.route('/historico', methods=['GET', 'POST'])
def historico():
    app.logger.debug('Página de historico acessada')
    if request.method == 'POST':
        # Obter as datas de início e fim do formulário
        data_inicio_str = request.form['data_inicio']
        data_fim_str = request.form['data_fim']

        # Converter as datas de string para o formato "yyyy-mm-dd"
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')

        app.logger.debug(f'Data de início convertida: {data_inicio}')
        app.logger.debug(f'Data de fim convertida: {data_fim}')


        # Verificar se cada dado histórico tem a chave 'data' como objeto datetime
        for dado in dados_historicos:
            if not isinstance(dado['data'], datetime):
                dado['data'] = datetime.fromisoformat(dado['data'])

        # Filtrar os dados históricos com base nas datas de início e fim
        dados_filtrados = []
        for dado in dados_historicos:
            data_dado = dado['data']

            # Verificar se a data do dado está dentro do intervalo de datas
            if data_inicio <= data_dado <= data_fim.replace(hour=23, minute=59, second=59):
                dados_filtrados.append(dado)

        app.logger.debug(f'Dados filtrados: {dados_filtrados}')

        # Por fim, renderize a página de histórico de temperaturas com os dados filtrados
        return render_template('backups/historico.html', dados=dados_filtrados)

    # Se for uma solicitação GET, simplesmente renderize a página com o formulário
    return render_template('backups/historico.html', dados=dados_historicos)


@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    # Buscar todos os resumos de uma vez
    dados_resumo_horario = sensor_db.relatorios_tabela_resumo_horario()
    dados_resumo_diario = sensor_db.relatorios_tabela_resumo_diario()
    dados_resumo_semanal = sensor_db.relatorios_tabela_resumo_semanal()
    dados_resumo_mensal = sensor_db.relatorios_tabela_resumo_mensal()  # Assumindo que você implementará esta função
    dados_resumo_anual = sensor_db.relatorios_tabela_resumo_anual()  # Assumindo que você implementará esta função

    # Passar todos os conjuntos de dados para o template
    return render_template('relatorios.html', dados_resumo_horario=dados_resumo_horario, dados_resumo_diario=dados_resumo_diario, dados_resumo_semanal=dados_resumo_semanal, dados_resumo_mensal=dados_resumo_mensal, dados_resumo_anual=dados_resumo_anual)


@app.route('/api/sensor_data', methods=['POST'])
def sensor_data_api():
    global temperatura_atual, humidade_atual, dados_historicos  # Acesso às variáveis globais
    global ultima_insercao_temp_hum

    try:
        data = request.get_json()

        app.logger.debug('Dados do sensor recebidos rota /api/sensor_data: %s', data)  # Registra os dados recebidos

        # Processar os dados do sensor
        temperatura_atual = data['temperatura']
        humidade_atual = data['humidade']

        # Obter a data atual como um objeto datetime
        data_atual = datetime.now()

        # Atualiza a lista de dados históricos para o dashboard em tempo real
        dados_historicos.append({
            'data': data_atual,
            'temperatura': temperatura_atual,
            'humidade': humidade_atual
        })

        # Inserção na base de dados de 15 em 15 mins
        #sensor_db.inserir_dados_temp_hum(data['data_hora'], data['temperatura'], data['humidade'])

        # Verifica se já passaram 15 minutos desde a última inserção
        if ultima_insercao_temp_hum is None or (data_atual - ultima_insercao_temp_hum).total_seconds() >= 900:
            sensor_db.inserir_dados_temp_hum(data['data_hora'], data['temperatura'], data['humidade'])
            ultima_insercao_temp_hum = data_atual
            app.logger.debug('Dados inseridos na base de dados na rota /api/sensor_data')

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
        app.logger.debug('Dados de Luz recebidos rota /api/sensor_lux_data: %s', data)

        luminosidade_atual = data['luminosidade']

        data_atual = datetime.now()

        # Atualizar a lista de dados históricos
        dados_historicos_lux.append({
            'data': data_atual,
            'luminosidade': luminosidade_atual
        })

        # Inserir os dados Luz na base de dados 15 em 15 mins
        #sensor_db.inserir_dados_luminosidade(data['data_hora'], data['luminosidade'])

        # Verifica se já passaram 15 minutos desde a última inserção
        if ultima_insercao_lux is None or (data_atual - ultima_insercao_lux).total_seconds() >= 900:
            sensor_db.inserir_dados_luminosidade(data['data_hora'], data['luminosidade'])
            ultima_insercao_lux = data_atual
            app.logger.debug('Dados de luminosidade inseridos na base de dados na rota /api/sensor_lux_data')

        return jsonify({'message': 'requisicao POST /api/sensor_lux_data sucesso e dados do sensor bh1750 recebidos corretamente'}), 200
    except Exception as e:
        app.logger.error('Erro ao processar dados na rota /api/sensor_lux_data: %s', e, exc_info=True)
        return jsonify({'error': 'Erro ao processar dados'}), 500

@app.route('/api/tempo_real')
def dados_tempo_real():
    # Supondo que temperatura_atual e humidade_atual são variáveis globais atualizadas por outra rota
    global temperatura_atual, humidade_atual, luminosidade_atual
    data = {
        'temperatura': temperatura_atual,
        'humidade': humidade_atual,
        'luminosidade': luminosidade_atual  # Adicione isso
    }
    app.logger.debug(f"Retorno de dados em tempo real rota /api/tempo_real: {data}")
    return jsonify(data)



@app.route('/notificacoes')
def notificacoes():
    from models import Orquidea
    orquideas = Orquidea.query.all()
    return render_template('notificacoes.html', orquideas=orquideas)


@app.route('/gravar-configuracoes-alerta', methods=['POST'])
def gravar_configuracoes_alerta():
    user_id = current_user.id
    orquidea_id = request.form['orquidea_id']
    temp_min = float(request.form['temp_min'])
    temp_max = float(request.form['temp_max'])
    humidade_min = float(request.form['humidade_min'])
    humidade_max = float(request.form['humidade_max'])

    # Criar um novo objeto de configuração do usuário
    nova_configuracao = UserConfig(
        user_id=user_id,
        orquidea_id=orquidea_id,
        temp_min=temp_min,
        temp_max=temp_max,
        humidade_min=humidade_min,
        humidade_max=humidade_max
    )

    # Adicionar a nova configuração à sessão do banco de dados
    db.session.add(nova_configuracao)
    # Salvar as alterações no banco de dados
    db.session.commit()

    return redirect(url_for('notificacoes'))







@app.route('/api/get-historic-data')
def get_historic_data():
    """Endpoint para recuperar dados do sensor."""
    registos = sensor_db.recuperar_dados_sensor()
    # Transformar os dados para o formato JSON
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
def dados_horario():
    dados_graficos = sensor_db.relatorios_grafico_resumo_horario()  # Buscando os dados através da função na sua biblioteca
    # Preparação dos dados para a resposta
    labels = [f'{resultado[1]}h' for resultado in dados_graficos]  # Horas como labels
    temp_maximas = [resultado[2] for resultado in dados_graficos]
    temp_minimas = [resultado[3] for resultado in dados_graficos]
    temp_medias = [resultado[4] for resultado in dados_graficos]
    hum_maximas = [resultado[5] for resultado in dados_graficos]
    hum_minimas = [resultado[6] for resultado in dados_graficos]
    hum_medias = [resultado[7] for resultado in dados_graficos]

    return jsonify({
        'labels': labels,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias
    })

@app.route('/api/dados/diario')
def dados_diario():
    dados_graficos = sensor_db.relatorios_grafico_resumo_diario()
    labels_diario = [resultado[0].strftime('%Y-%m-%d') for resultado in dados_graficos]
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_diario,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias
    })

@app.route('/api/dados/semanal')
def dados_semanal():
    dados_graficos = sensor_db.relatorios_grafico_resumo_semanal()
    labels_semanal = [f'Semana {resultado[0]}' for resultado in dados_graficos]  # Supondo que [0] seja o número da semana
    temp_maximas = [resultado[1] for resultado in dados_graficos]  # Supondo que [1] seja a temperatura máxima
    temp_minimas = [resultado[2] for resultado in dados_graficos]  # Supondo que [2] seja a temperatura mínima
    temp_medias = [resultado[3] for resultado in dados_graficos]  # Supondo que [3] seja a temperatura média
    hum_maximas = [resultado[4] for resultado in dados_graficos]  # Supondo que [4] seja a humidade máxima
    hum_minimas = [resultado[5] for resultado in dados_graficos]  # Supondo que [5] seja a humidade mínima
    hum_medias = [resultado[6] for resultado in dados_graficos]  # Supondo que [6] seja a humidade média

    return jsonify({
        'labels': labels_semanal,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias
    })

@app.route('/api/dados/mensal')
def dados_mensal():
    dados_graficos = sensor_db.relatorios_grafico_resumo_mensal()
    labels_mensal = [f'Mês {resultado[0]}' for resultado in dados_graficos]  # Simplesmente prefixamos com 'Mês'
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_mensal,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias
    })


@app.route('/api/dados/anual')
def dados_anual():
    dados_graficos = sensor_db.relatorios_grafico_resumo_anual()
    labels_anual = [f'Ano {resultado[0]}' for resultado in dados_graficos]  # Prefixando com 'Ano'
    temp_maximas = [resultado[1] for resultado in dados_graficos]
    temp_minimas = [resultado[2] for resultado in dados_graficos]
    temp_medias = [resultado[3] for resultado in dados_graficos]
    hum_maximas = [resultado[4] for resultado in dados_graficos]
    hum_minimas = [resultado[5] for resultado in dados_graficos]
    hum_medias = [resultado[6] for resultado in dados_graficos]

    return jsonify({
        'labels': labels_anual,
        'temperaturas_maximas': temp_maximas,
        'temperaturas_minimas': temp_minimas,
        'temperaturas_medias': temp_medias,
        'humidades_maximas': hum_maximas,
        'humidades_minimas': hum_minimas,
        'humidades_medias': hum_medias
    })


@app.route('/export/excel')
def export_excel():
    # Simulando dados
    dados = {
        'Coluna1': [1, 2, 3, 4, 5],
        'Coluna2': ['A', 'B', 'C', 'D', 'E']
    }

    # Convertendo para DataFrame
    df = pd.DataFrame(dados)

    # Salvando o DataFrame em um arquivo Excel
    filename = 'dados.xlsx'
    df.to_excel(filename, index=False)

    # Enviando o arquivo para download
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
        # Assuma que você tem um usuário e configurações fictícias para o teste
        fake_user_email = "dinis.duarte@my.istec.pt"
        fake_config = {
            'temp_min': 15,
            'temp_max': 25,
            'humidade_min': 30,
            'humidade_max': 70
        }
        fake_data = {
            'temperature': 26,  # Acima do temp_max para disparar o alerta
            'humidity': 80       # Acima do humidade_max para disparar o alerta
        }
        send_alert_email(fake_user_email, fake_config, fake_data)
        return 'E-mail de alerta enviado com sucesso!'
    except Exception as e:
        return f'Erro ao enviar e-mail de alerta: {str(e)}'

# Adiciona uma rota de teste em app.py
@app.route('/test-alerts')
def test_alerts():
    try:
        # Chama a função diretamente
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
        # Faça todas as inicializações que requerem o contexto da aplicação aqui
        db.create_all()  # Se você estiver usando SQLAlchemy para inicializar o banco de dados
        # Inicializa a variável com o último registro de luminosidade
        ultima_insercao_lux = sensor_db.ultimo_registo_lux()
        if ultima_insercao_lux is None:
            ultima_insercao_lux = datetime.now()
        ultima_insercao_temp_hum = sensor_db.ultimo_registo_temp_hum()
        if ultima_insercao_temp_hum is None:
            ultima_insercao_temp_hum = datetime.now()
    # Iniciar o agendador antes de executar a aplicação
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)