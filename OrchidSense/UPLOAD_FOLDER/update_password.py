# update_password.py
from hashing import gerar_hash_scrypt
from users_database import atualizar_senha_usuario

def trocar_senha_usuario(user_id, nova_senha):
    nova_senha_hash = gerar_hash_scrypt(nova_senha)
    if atualizar_senha_usuario(user_id, nova_senha_hash):
        print("Senha atualizada com sucesso!")
    else:
        print("Erro ao atualizar a senha.")

# Exemplo de uso
if __name__ == "__main__":
    user_id = 3  # ID do usuário para quem você quer mudar a senha
    nova_senha = "managerorchidsenseP@ssw0rd"  # Substitua pela nova senha desejada

    trocar_senha_usuario(user_id, nova_senha)
