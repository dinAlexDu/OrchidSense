import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def conectar():
    """ Função para conectar à base de dados. """
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            database='sensor_data_db',
            user='root',
            password=''
        )
        return conn
    except Error as e:
        print("Erro ao conectar ao MySQL", e)

def ultimo_registo_hora():
    """Retorna a data e hora do último registro."""
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT data_hora FROM dados_historicos ORDER BY data_hora DESC LIMIT 1")
        ultimo_registo = cursor.fetchone()
        cursor.close()
        conn.close()
        if ultimo_registo:
            return ultimo_registo[0]
        else:
            return None



def inserir_dados_sensor_hora(data_hora, temperatura, humidade):
    """Insere dados na base de dados se passou uma hora desde o último registro."""
    ultimo_registo = ultimo_registo_hora()
    data_hora_atual = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
    # if not ultimo_registo or data_hora_atual - ultimo_registo >= timedelta(hours=1):
    if not ultimo_registo or data_hora_atual - ultimo_registo >= timedelta(minutes=10):
        conn = conectar()
        if conn.is_connected():
            cursor = conn.cursor()
            query = "INSERT INTO dados_historicos (data_hora, temperatura, humidade) VALUES (%s, %s, %s)"
            values = (data_hora, temperatura, humidade)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()

def recuperar_dados_sensor():
    """Recupera os dados mais recentes da base de dados."""
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        query = "SELECT * FROM dados_historicos ORDER BY data_hora DESC LIMIT 100"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados


def recuperar_dados_sensor_ultimas_24_horas():
    """Recupera os dados das últimas 24 horas da base de dados, assumindo um registro por hora."""
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        # Limitar a 24 registros assumindo que temos um registro por hora
        query = "SELECT * FROM dados_historicos WHERE data_hora > NOW() - INTERVAL 24 HOUR ORDER BY data_hora ASC"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados

def relatorios_resumo_diario():
    """Resumo diário dos dados de temperatura e humidade."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(data_hora) AS dia, 
                MAX(temperatura) AS temp_maxima, 
                MIN(temperatura) AS temp_minima, 
                AVG(temperatura) AS temp_media,
                MAX(humidade) AS hum_maxima,
                MIN(humidade) AS hum_minima,
                AVG(humidade) AS hum_media
            FROM dados_historicos
            WHERE data_hora >= CURDATE()
            GROUP BY dia
        """)
        resultados = cursor.fetchall()
        # Convertendo resultados em dicionários
        chaves = ['dia', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media']
        dados = [dict(zip(chaves, resultado)) for resultado in resultados]
        cursor.close()
        conn.close()
        return dados
    except Error as e:
        print("Erro ao pesquisar o relatório diário", e)
        return []

def relatorios_semanal():
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        # Ajuste a query para calcular médias, máximos e mínimos semanais
        query = """
        SELECT DATE(data_hora) AS data, AVG(temperatura) AS media_temperatura, AVG(humidade) AS media_humidade
        FROM dados_historicos
        WHERE data_hora > NOW() - INTERVAL 1 WEEK
        GROUP BY DATE(data_hora)
        ORDER BY DATE(data_hora);
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados


def relatorios_resumo_semanal():
    """Resumo semanal dos dados de temperatura e humidade."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                YEAR(data_hora) AS ano, 
                WEEK(data_hora) AS semana, 
                MAX(temperatura) AS temp_maxima, 
                MIN(temperatura) AS temp_minima, 
                AVG(temperatura) AS temp_media,
                MAX(humidade) AS hum_maxima,
                MIN(humidade) AS hum_minima,
                AVG(humidade) AS hum_media
            FROM dados_historicos
            WHERE data_hora >= CURDATE() - INTERVAL 1 WEEK
            GROUP BY ano, semana;
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(zip(['semana', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media'], resultado)) for resultado in resultados]
    except Error as e:
        print("Erro ao pesquisar o relatório semanal", e)
        return []

def relatorios_resumo_mensal():
    """Resumo mensal dos dados de temperatura e humidade."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                MONTH(data_hora) AS mes, 
                MAX(temperatura) AS temp_maxima, 
                MIN(temperatura) AS temp_minima, 
                AVG(temperatura) AS temp_media,
                MAX(humidade) AS hum_maxima,
                MIN(humidade) AS hum_minima,
                AVG(humidade) AS hum_media
            FROM dados_historicos
            WHERE data_hora >= CURDATE() - INTERVAL 1 MONTH
            GROUP BY mes
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(zip(['mes', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media'], resultado)) for resultado in resultados]
    except Error as e:
        print("Erro ao pesquisar o relatório mensal", e)
        return []

def relatorios_resumo_anual():
    """Resumo anual dos dados de temperatura e humidade."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                YEAR(data_hora) AS ano, 
                MAX(temperatura) AS temp_maxima, 
                MIN(temperatura) AS temp_minima, 
                AVG(temperatura) AS temp_media,
                MAX(humidade) AS hum_maxima,
                MIN(humidade) AS hum_minima,
                AVG(humidade) AS hum_media
            FROM dados_historicos
            WHERE data_hora >= CURDATE() - INTERVAL 1 YEAR
            GROUP BY ano
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(zip(['ano', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media'], resultado)) for resultado in resultados]
    except Error as e:
        print("Erro ao pesquisar o relatório anual", e)
        return []
