from werkzeug.security import generate_password_hash

nova_senha = 'userorchidsenseP@ssw0rd'  # Substitua pela nova senha desejada
novo_hash = generate_password_hash(nova_senha)

print(novo_hash)
