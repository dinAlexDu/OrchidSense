import mysql.connector


def obter_dados_orquideas():
    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(
            user='root',
            password='mariadbp4r4s1t1s',  # Substitua com a sua senha real
            host='127.0.0.1',
            database='orquideas_db'
        )

        # Criar um cursor para executar comandos no banco de dados
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orquideas")

        # Buscar todos os dados retornados
        dados_orquideas = cursor.fetchall()

        # Fechar o cursor e a conexão
        cursor.close()
        conn.close()

        return dados_orquideas

    except mysql.connector.Error as err:
        print(f"Erro ao acessar o banco de dados: {err}")
        return []
