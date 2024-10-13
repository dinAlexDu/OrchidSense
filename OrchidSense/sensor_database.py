import logging
import mysql.connector
from mysql.connector import Error


from datetime import datetime, timedelta

# Function to establish a connection to the MySQL database.
def conectar():
    try:
        # Attempt to connect to the MySQL database using the given credentials.
        conn = mysql.connector.connect(
            host='127.0.0.1',  # The database host (localhost in this case)
            database='orchidsense_db',  # The name of the database
            user='pma',  # The database user
            password='NtxFL6ms7pn3zRK2G9feDy'  # The database password
        )
        return conn  # Return the connection object if successful.
    except Error as e:
        # If there's an error during the connection, print an error message.
        print("Erro ao ligar ao MySQL", e)


def ultimo_registo_temp_hum():
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT data_hora FROM sensor_data ORDER BY data_hora DESC LIMIT 1")
        ultimo_registo = cursor.fetchone()
        cursor.close()
        conn.close()
        if ultimo_registo:
            return ultimo_registo[0]
        else:
            return None


def ultimo_registo_lux():
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT data_hora FROM sensor_lux_data ORDER BY data_hora DESC LIMIT 1")
        ultimo_registo = cursor.fetchone()
        cursor.close()
        conn.close()
        if ultimo_registo:
            return ultimo_registo[0]
        else:
            return None




def inserir_dados_temp_hum(data_hora, temperatura, humidade):
    conn = conectar()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            query = "INSERT INTO sensor_data (data_hora, temperatura, humidade) VALUES (%s, %s, %s)"
            values = (data_hora, temperatura, humidade)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            print("Dados de Temperatura e Humidade inseridos na BD.")
        except Error as e:
            print(f"Erro ao inserir dados Temp. e Hum. na BD: {e}")
        finally:
            conn.close()
    else:
        print("Falha ao ligar à BD.")


def inserir_dados_luminosidade(data_hora, luminosidade):
    conn = conectar()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            query = "INSERT INTO sensor_lux_data (data_hora, luminosidade) VALUES (%s, %s)"
            values = (data_hora, luminosidade)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            print("Dados de luz inseridos com sucesso na BD.")
        except Error as e:
            print(f"Erro ao inserir dados luz na base de dados: {e}")
        finally:
            conn.close()
    else:
        print("Falha ao ligar à base de dados.")



def recuperar_dados_sensor():
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        query = "SELECT * FROM sensor_data ORDER BY data_hora DESC LIMIT 100"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados


def query_dados_sensor_temp_hum_ultimas_24_horas():
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        query = "SELECT data_hora, temperatura, humidade FROM sensor_data WHERE data_hora >= NOW() - INTERVAL 1 DAY ORDER BY data_hora DESC LIMIT 24"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        logging.debug(f"Resultados Temp e Hum: {resultados}")  # Usando logging em vez de print
        return resultados


def query_dados_sensor_luminosidade_ultimas_24_horas():
    conn = conectar()
    if conn.is_connected():
        cursor = conn.cursor()
        query = "SELECT data_hora, luminosidade FROM sensor_lux_data WHERE data_hora >= NOW() - INTERVAL 1 DAY ORDER BY data_hora DESC LIMIT 24"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados


def relatorios_grafico_resumo_horario():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(sensor_data.data_hora) AS dia, 
                HOUR(sensor_data.data_hora) AS hora, 
                MAX(sensor_data.temperatura) AS temp_maxima, 
                MIN(sensor_data.temperatura) AS temp_minima, 
                AVG(sensor_data.temperatura) AS temp_media, 
                MAX(sensor_data.humidade) AS hum_maxima, 
                MIN(sensor_data.humidade) AS hum_minima, 
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data 
            ON sensor_lux_data.data_hora BETWEEN sensor_data.data_hora - INTERVAL 10 SECOND AND sensor_data.data_hora + INTERVAL 10 SECOND
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 1 DAY
            GROUP BY dia, hora
            ORDER BY dia ASC, hora ASC;
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Error as e:
        print("Erro ao pesquisar o relatório horário", e)
        return []

def relatorios_grafico_resumo_diario():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                DATE(sensor_data.data_hora) AS dia,
                MAX(sensor_data.temperatura) AS temp_maxima,
                MIN(sensor_data.temperatura) AS temp_minima,
                AVG(sensor_data.temperatura) AS temp_media,
                MAX(sensor_data.humidade) AS hum_maxima,
                MIN(sensor_data.humidade) AS hum_minima,
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora BETWEEN sensor_data.data_hora - INTERVAL 10 SECOND AND sensor_data.data_hora + INTERVAL 10 SECOND
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 30 DAY
            GROUP BY DATE(sensor_data.data_hora)
            ORDER BY dia ASC;
        """)
        resultados = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return resultados

def relatorios_grafico_resumo_semanal():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                WEEK(sensor_data.data_hora) AS semana, 
                MAX(sensor_data.temperatura) AS temp_maxima, 
                MIN(sensor_data.temperatura) AS temp_minima, 
                AVG(sensor_data.temperatura) AS temp_media, 
                MAX(sensor_data.humidade) AS hum_maxima, 
                MIN(sensor_data.humidade) AS hum_minima, 
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora BETWEEN sensor_data.data_hora - INTERVAL 10 SECOND AND sensor_data.data_hora + INTERVAL 10 SECOND
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 1 YEAR
            GROUP BY semana
            ORDER BY semana ASC
            LIMIT 52;
        """)
        dados = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return dados


def relatorios_grafico_resumo_anual():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            YEAR(sensor_data.data_hora) AS ano, 
            MAX(sensor_data.temperatura) AS temp_maxima, 
            MIN(sensor_data.temperatura) AS temp_minima, 
            AVG(sensor_data.temperatura) AS temp_media,
            MAX(sensor_data.humidade) AS hum_maxima,
            MIN(sensor_data.humidade) AS hum_minima,
            AVG(sensor_data.humidade) AS hum_media,
            MAX(sensor_lux_data.luminosidade) AS lux_maxima,
            MIN(sensor_lux_data.luminosidade) AS lux_minima,
            AVG(sensor_lux_data.luminosidade) AS lux_media
        FROM sensor_data
        LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora = sensor_data.data_hora
        GROUP BY ano
        ORDER BY ano ASC
    """)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados


def relatorios_grafico_resumo_mensal():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            DATE_FORMAT(sensor_data.data_hora, '%Y-%m') AS mes,
            MAX(sensor_data.temperatura) AS temp_maxima, 
            MIN(sensor_data.temperatura) AS temp_minima, 
            AVG(sensor_data.temperatura) AS temp_media,
            MAX(sensor_data.humidade) AS hum_maxima,
            MIN(sensor_data.humidade) AS hum_minima,
            AVG(sensor_data.humidade) AS hum_media,
            MAX(sensor_lux_data.luminosidade) AS lux_maxima,
            MIN(sensor_lux_data.luminosidade) AS lux_minima,
            AVG(sensor_lux_data.luminosidade) AS lux_media
        FROM sensor_data
        LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora = sensor_data.data_hora
        WHERE sensor_data.data_hora >= NOW() - INTERVAL 12 MONTH
        GROUP BY mes
        ORDER BY mes ASC
    """)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados



def relatorios_tabela_resumo_horario():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(sensor_data.data_hora) AS dia, 
                HOUR(sensor_data.data_hora) AS hora, 
                MAX(sensor_data.temperatura) AS temp_maxima, 
                MIN(sensor_data.temperatura) AS temp_minima, 
                AVG(sensor_data.temperatura) AS temp_media, 
                MAX(sensor_data.humidade) AS hum_maxima, 
                MIN(sensor_data.humidade) AS hum_minima, 
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora BETWEEN sensor_data.data_hora - INTERVAL 10 SECOND AND sensor_data.data_hora + INTERVAL 10 SECOND
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 1 DAY
            GROUP BY dia, hora
            ORDER BY dia ASC, hora ASC;
        """)
        resultados = cursor.fetchall()
        dados = [{
            'dia': resultado[0],
            'hora': resultado[1],
            'temp_maxima': resultado[2],
            'temp_minima': resultado[3],
            'temp_media': resultado[4],
            'hum_maxima': resultado[5],
            'hum_minima': resultado[6],
            'hum_media': resultado[7],
            'lux_maxima': resultado[8],
            'lux_minima': resultado[9],
            'lux_media': resultado[10]
        } for resultado in resultados]
        cursor.close()
        conn.close()
        return dados
    except Error as e:
        print("Erro ao pesquisar o relatório horário", e)
        return []




def relatorios_tabela_resumo_diario():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                DATE(sensor_data.data_hora) AS dia,
                MAX(sensor_data.temperatura) AS temp_maxima,
                MIN(sensor_data.temperatura) AS temp_minima,
                AVG(sensor_data.temperatura) AS temp_media,
                MAX(sensor_data.humidade) AS hum_maxima,
                MIN(sensor_data.humidade) AS hum_minima,
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data ON DATE(sensor_data.data_hora) = DATE(sensor_lux_data.data_hora)
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 30 DAY
            GROUP BY dia
            ORDER BY dia ASC;
        """)
        resultados = cursor.fetchall()
        chaves = ['dia', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media', 'lux_maxima', 'lux_minima', 'lux_media']
        dados = [dict(zip(chaves, resultado)) for resultado in resultados]
        cursor.close()
        conn.close()
        return dados
    except Error as e:
        print("Erro ao pesquisar o relatório diário", e)
        return []

def relatorios_tabela_resumo_semanal():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                WEEK(sensor_data.data_hora) AS semana, 
                MAX(sensor_data.temperatura) AS temp_maxima, 
                MIN(sensor_data.temperatura) AS temp_minima, 
                AVG(sensor_data.temperatura) AS temp_media, 
                MAX(sensor_data.humidade) AS hum_maxima, 
                MIN(sensor_data.humidade) AS hum_minima, 
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data 
            LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora BETWEEN sensor_data.data_hora - INTERVAL 10 SECOND AND sensor_data.data_hora + INTERVAL 10 SECOND
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 1 YEAR
            GROUP BY semana
            ORDER BY semana ASC
            LIMIT 52;
        """)
        resultados = cursor.fetchall()
        chaves = ['semana', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media', 'lux_maxima', 'lux_minima', 'lux_media']
        dados = [dict(zip(chaves, resultado)) for resultado in resultados]
        cursor.close()
        conn.close()
        return dados
    except Error as e:
        print("Erro ao pesquisar o relatório semanal", e)
        return []


def relatorios_tabela_resumo_mensal():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                DATE_FORMAT(sensor_data.data_hora, '%Y-%m') AS mes,
                MAX(sensor_data.temperatura) AS temp_maxima, 
                MIN(sensor_data.temperatura) AS temp_minima, 
                AVG(sensor_data.temperatura) AS temp_media,
                MAX(sensor_data.humidade) AS hum_maxima,
                MIN(sensor_data.humidade) AS hum_minima,
                AVG(sensor_data.humidade) AS hum_media,
                COALESCE(MAX(sensor_lux_data.luminosidade), 0) AS lux_maxima,
                COALESCE(MIN(sensor_lux_data.luminosidade), 0) AS lux_minima,
                COALESCE(ROUND(AVG(sensor_lux_data.luminosidade)), 0) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora BETWEEN sensor_data.data_hora - INTERVAL 10 SECOND AND sensor_data.data_hora + INTERVAL 10 SECOND
            WHERE sensor_data.data_hora >= NOW() - INTERVAL 12 MONTH
            GROUP BY mes
            ORDER BY mes ASC
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(zip(['mes', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media', 'lux_maxima', 'lux_minima', 'lux_media'],
                         resultado)) for resultado in resultados]
    except Error as e:
        print("Erro ao pesquisar o relatório mensal", e)
        return []

def relatorios_tabela_resumo_anual():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                YEAR(sensor_data.data_hora) AS ano, 
                MAX(sensor_data.temperatura) AS temp_maxima, 
                MIN(sensor_data.temperatura) AS temp_minima, 
                AVG(sensor_data.temperatura) AS temp_media,
                MAX(sensor_data.humidade) AS hum_maxima,
                MIN(sensor_data.humidade) AS hum_minima,
                AVG(sensor_data.humidade) AS hum_media,
                MAX(sensor_lux_data.luminosidade) AS lux_maxima,
                MIN(sensor_lux_data.luminosidade) AS lux_minima,
                AVG(sensor_lux_data.luminosidade) AS lux_media
            FROM sensor_data
            LEFT JOIN sensor_lux_data ON sensor_lux_data.data_hora = sensor_data.data_hora
            GROUP BY ano
            ORDER BY ano ASC
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(zip(['ano', 'temp_maxima', 'temp_minima', 'temp_media', 'hum_maxima', 'hum_minima', 'hum_media', 'lux_maxima', 'lux_minima', 'lux_media'],
                         resultado)) for resultado in resultados]
    except Error as e:
        print("Erro ao pesquisar o relatório anual", e)
        return []

def get_sensor_data_last_hour():
    conn = conectar()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)

            # Query para obter dados de temperatura e humidade das últimas 60 minutos
            query_temp_hum = """
            SELECT temperatura, humidade, data_hora
            FROM sensor_data
            WHERE data_hora >= NOW() - INTERVAL 1 HOUR;
            """
            cursor.execute(query_temp_hum)
            results_temp_hum = cursor.fetchall()

            # Query para obter dados de luminosidade das últimas 60 minutos
            query_lux = """
            SELECT luminosidade, data_hora
            FROM sensor_lux_data
            WHERE data_hora >= NOW() - INTERVAL 1 HOUR;
            """
            cursor.execute(query_lux)
            results_lux = cursor.fetchall()

            cursor.close()
            conn.close()

            if results_temp_hum and results_lux:
                return results_temp_hum, results_lux
            else:
                return None, None
        except Error as e:
            print("Erro ao executar a query:", e)
            return None, None
    else:
        print("Falha na ligação à base de dados")
        return None, None



def get_latest_sensor_data():
    conn = conectar()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)

            # Query temperatura e humidade
            query_temp_hum = """
            SELECT temperatura, humidade, data_hora
            FROM sensor_data
            ORDER BY data_hora DESC
            LIMIT 1;
            """
            cursor.execute(query_temp_hum)
            result_temp_hum = cursor.fetchone()

            # Query luminosidade
            query_lux = """
            SELECT luminosidade, data_hora
            FROM sensor_lux_data
            ORDER BY data_hora DESC
            LIMIT 1;
            """
            cursor.execute(query_lux)
            result_lux = cursor.fetchone()

            cursor.close()
            conn.close()

            if result_temp_hum and result_lux:
                return {
                    'temperatura': result_temp_hum['temperatura'],
                    'humidade': result_temp_hum['humidade'],
                    'luminosidade': result_lux['luminosidade'],
                    'data_hora': result_temp_hum['data_hora']  # Supondo que os timestamps são sincronizados
                }
            else:
                return None
        except Error as e:
            print("Erro ao executar a query:", e)
            return None
    else:
        print("Falha na ligação à base de dados")
        return None

