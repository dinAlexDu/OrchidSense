import logging
import mysql.connector
from mysql.connector import Error

# Function to establish a connection to the MySQL database.
def conectar():
    try:
        # Attempt to connect to the MySQL database using the provided credentials.
        conn = mysql.connector.connect(
            host='127.0.0.1',  # Database host (localhost)
            database='orchidsense_db',  # Name of the database
            user='pma',  # Username to connect to the database
            password='NtxFL6ms7pn3zRK2G9feDy'  # Password for the user
        )
        return conn  # Return the connection object if successful.
    except Error as e:
        # Log an error message if the connection fails.
        logging.error(f"Erro ao conectar ao MySQL: {e}")
        return None  # Return None if the connection fails.

# Function to retrieve a user from the database by their user ID.
def obter_dados_utilizadores():
    try:
        conn = conectar()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, profile_image, is_admin FROM users')
        users = cursor.fetchall()
        conn.close()
        return users
    except Error as e:
        logging.error(f"Erro ao obter dados dos utilizadores: {e}")
        if conn:
            conn.close()
        return []

# Function to retrieve a user from the database based on their email address.
def obter_utilizador_por_email(email):
    try:
        conn = conectar()
        if conn is None:
            return None

        cursor = conn.cursor()
        cursor.execute('SELECT id, email, password_hash, first_name, last_name, profile_image, is_admin FROM users WHERE email = %s', (email,))
        utilizador = cursor.fetchone()
        conn.close()
        return utilizador
    except Error as e:
        logging.error(f"Erro ao obter dados do utilizador: {e}")
        if conn:
            conn.close()
        return None

# Function to retrieve a user from the database based on their user ID.
def obter_utilizador_por_id(user_id):
    try:
        conn = conectar()
        if conn is None:
            return None

        cursor = conn.cursor()
        cursor.execute('SELECT id, email, password_hash, first_name, last_name, profile_image, is_admin FROM users WHERE id = %s', (user_id,))
        utilizador = cursor.fetchone()
        conn.close()
        return utilizador
    except Error as e:
        logging.error(f"Erro ao obter dados do utilizador: {e}")
        if conn:
            conn.close()
        return None