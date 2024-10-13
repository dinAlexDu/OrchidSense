# verify_password.py
from hashing import verificar_senha
from users_database import obter_usuario_por_email

email = "manager.orchidsense@outlook.com"  # Email do usuário para quem você quer verificar a senha
senha = "managerorchidsenseP@ssw0rd"  # A senha que você quer verificar

print(f"Tentando obter dados do usuário para email: {email} ({repr(email)})")  # Depuração
user_data = obter_usuario_por_email(email)
print(f"Dados do usuário obtidos: {user_data}")  # Depuração
if user_data:
    hash_armazenado = user_data['password_hash']
    print(f"Hash armazenado: {hash_armazenado}")

    try:
        if verificar_senha(senha, hash_armazenado):
            print("Senha correta!")
        else:
            print("Senha incorreta.")
    except ValueError as e:
        print(f"Erro ao verificar a senha: {e}")
else:
    print("Usuário não encontrado ou erro ao obter o hash da senha.")
