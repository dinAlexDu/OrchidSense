import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta  # Importe a classe datetime
from orquideas_database import obter_dados_orquideas  # Importa a função do arquivo database.py
import sensor_database as db


logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

# Configurar o logger
#logging.basicConfig(filename='app.log', level=logging.DEBUG)

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
    # Os dados em tempo real são mantidos conforme recebidos pelo simulate_sensor_data.py


    # Para os gráficos, usamos os dados armazenados na base de dados das últimas 24 horas
    dados_graficos = sensor_db.recuperar_dados_sensor_ultimas_24_horas()

    labels = [registro[1].strftime('%H:%M') for registro in dados_graficos]
    temperaturas_grafico = [registro[2] for registro in dados_graficos]
    humidades_grafico = [registro[3] for registro in dados_graficos]

    # A função render_template passa tanto os dados em tempo real quanto os dados para os gráficos
    return render_template('dashboard.html',
                           temperatura_atual=temperatura_atual,
                           humidade_atual=humidade_atual,
                           labels=labels,
                           temperaturas=temperaturas_grafico,
                           humidades=humidades_grafico)


# @app.route('/dashboard')
# def dashboard():
#     app.logger.debug('Página de dashboard acessada')
#     # Dados em tempo real, continuam sendo atualizados pelo simulate_sensor_data.py
#
#
#     # Busca dados das últimas 24 horas da base de dados
#     dados_graficos = db.recuperar_dados_sensor_ultimas_24_horas()
#
#     # Preparação dos dados para o gráfico
#     labels = [registro[1].strftime('%H:%M') for registro in dados_graficos]
#     temperaturas_grafico = [registro[2] for registro in dados_graficos]
#     humidades_grafico = [registro[3] for registro in dados_graficos]
#
#     return render_template('dashboard.html', temperatura_atual=temperatura_atual, humidade_atual=humidade_atual, labels=labels, temperaturas=temperaturas_grafico, humidades=humidades_grafico)
#
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

    data = request.get_json()

    app.logger.debug('Dados do sensor recebidos: %s', data)  # Registra os dados recebidos

    # Processar os dados do sensor recebidos
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



    # Inserção na base de dados de hora em hora
    sensor_db.inserir_dados_sensor_hora(data['data_hora'], data['temperatura'], data['humidade'])
    return jsonify({'message': 'Dados do sensor recebidos com sucesso'}), 200







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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

