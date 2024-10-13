import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta  # Importe a classe datetime
from orquideas_database import obter_dados_orquideas  # Importa a função do arquivo database.py

import sensor_database as db
logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

# Configurar o logger
logging.basicConfig(level=logging.DEBUG)  # Define o nível de log como DEBUG

# Variáveis globais para armazenar os dados atuais do sensor
temperatura_atual = 0.0
humidade_atual = 0.0

# Inicialize uma lista vazia para armazenar os dados históricos
dados_historicos = []

@app.route('/')
def index():
    app.logger.debug('Página inicial acessada')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    app.logger.debug('Página de dashboard acessada')
    agora = datetime.now()
    um_dia_atras = agora - timedelta(days=1)
    dados_filtrados = [d for d in dados_historicos if um_dia_atras <= d['data'] <= agora]

    labels = [d['data'].strftime("%H:%M:%S") for d in dados_filtrados]
    temperaturas_grafico = [d['temperatura'] for d in dados_filtrados]
    humidades_grafico = [d['humidade'] for d in dados_filtrados]

    # Passa os dados em tempo real e os dados para os gráficos para o template
    return render_template('dashboard.html', temperatura_atual=temperatura_atual, humidade_atual=humidade_atual, labels=labels, temperaturas=temperaturas_grafico, humidades=humidades_grafico)


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
    if request.method == 'POST':
        # Lógica para tratar os filtros enviados pelo usuário
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        # Realizar a filtragem com base nas datas ou outros critérios
        dados_filtrados = filtrar_dados(data_inicio, data_fim)
        return render_template('relatorios.html', dados=dados_filtrados)
    else:
        # Simplesmente renderizar a página de relatórios com os filtros padrão ou sem dados
        return render_template('relatorios.html')




@app.route('/api/sensor_data', methods=['POST'])
def sensor_data_api():
    global temperatura_atual, humidade_atual, dados_historicos  # Acesso às variáveis globais

    data = request.get_json()

    app.logger.debug('Dados do sensor recebidos: %s', data)  # Registra os dados recebidos

    # Processar os dados do sensor recebidos
    temperatura_atual = data['temperatura']
    humidade_atual = data['humidade']

    # Obter a data atual como um objeto datetime
    data_atual = datetime.now()
    # data_atual = datetime.now()



    # Garantir que a chave 'data' seja um objeto datetime antes de adicioná-la aos dados históricos
    #data_atual_str = data_atual.strftime('%Y-%m-%d %H:%M:%S')
    # Converter a data para o formato ISO 8601
    # dataiso = data_atual.isoformat()


    # Armazenar os dados recebidos na lista de dados históricos
    dados_historicos.append({
        'data': data_atual,
        'temperatura': temperatura_atual,
        'humidade': humidade_atual
    })

    # Responder com uma mensagem de sucesso
    response_data = {'message': 'Dados do sensor recebidos com sucesso'}
    return jsonify(response_data), 200

# funcoes para o sensor da base de dados

@app.route('/api/dados-sensor', methods=['POST'])
def inserir_dados():
    data = request.get_json()
    db.inserir_dados_sensor(data['data_hora'], data['temperatura'], data['humidade'])
    return jsonify({'mensagem': 'Dados inseridos com sucesso'}), 201


@app.route('/api/dados-sensor')
def get_sensor_data():
    registros_brutos = db.recuperar_dados_sensor()

    # Converter os dados para um formato que possa ser serializado para JSON
    dados_transformados = []
    for registro in registros_brutos:
        dados_transformados.append({
            'id': registro[0],
            'data_hora': registro[1].strftime("%Y-%m-%d %H:%M:%S"),
            'temperatura': float(registro[2]),
            'humidade': float(registro[3])
        })

    return jsonify(dados_transformados)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

