import mysql.connector

# Function to fetch all orchid data from the 'orquideas' table in the database.
def obter_dados_orquideas():
    try:
        # Establish a connection to the database using MySQL connector.
        conn = mysql.connector.connect(
            user='pma',
            password='NtxFL6ms7pn3zRK2G9feDy',
            host='127.0.0.1',
            database='orchidsense_db'
        )

        # Create a cursor object to interact with the database.
        cursor = conn.cursor()

        # Execute a SQL query to retrieve all data from the 'orquideas' table.
        cursor.execute("SELECT * FROM orquideas")

        # Fetch all the results from the executed query.
        dados_orquideas = cursor.fetchall()

        # Close the cursor and the database connection after the query is executed.
        cursor.close()
        conn.close()

        # Return the fetched orchid data.
        return dados_orquideas

    # Handle any database-related errors.
    except mysql.connector.Error as err:
        print(f"Erro ao ligar à base de dados: {err}")  # Print the error message.
        return []  # Return an empty list if there's an error.



# Function to fetch user-specific alert configurations from the database.
def get_configs_alertas(user_id):
    try:
        # Establish a connection to the database using MySQL connector.
        conn = mysql.connector.connect(
            user='pma',
            password='NtxFL6ms7pn3zRK2G9feDy',
            host='127.0.0.1',
            database='orchidsense_db'
        )

        # Create a cursor object to interact with the database.
        cursor = conn.cursor()

        # SQL query to fetch the alert configurations for a specific user
        # by joining the 'user_configs' and 'orquideas' tables.
        query = """
            SELECT uc.id, o.nome, uc.temp_min, uc.temp_max, uc.humidade_min, uc.humidade_max, uc.lux_min, uc.lux_max
            FROM user_configs uc
            JOIN orquideas o ON uc.orquidea_id = o.id
            WHERE uc.user_id = %s
        """

        # Execute the SQL query with the provided user_id as a parameter.
        cursor.execute(query, (user_id,))

        # Fetch all the results from the executed query.
        configuracoes_alertas = cursor.fetchall()

        #  Close the cursor and the database connection after the query is executed.
        cursor.close()
        conn.close()

        # Return the fetched alert configurations for the user.
        return configuracoes_alertas

    # Handle any database-related errors.
    except mysql.connector.Error as err:
        print(f"Erro ao ligar à base de dados: {err}")
        return []

