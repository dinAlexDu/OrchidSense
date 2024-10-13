from werkzeug.security import check_password_hash

# O hash da senha do banco de dados para o usuário específico
password_hash = 'scrypt:16384:8:1$IMcl3h70Amni41U9swtIaw==$PtL6dRf/iAYw7UO2Uxg444grUHlr6cBHbpPmM5Pt9Cta/MIQUthLd+w+rD0c747cCNceimgkbP3dWxTELjosJg=='  # Coloque o hash completo aqui

# A senha que você deseja testar
senha_tentada = 'managerorchidsenseP@ssw0rd'  # Substitua pela senha que você deseja testar

if check_password_hash(password_hash, senha_tentada):
    print("Senha correta")
else:
    print("Senha incorreta")
