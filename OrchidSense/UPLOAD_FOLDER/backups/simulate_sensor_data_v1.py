import requests
import random
import time

# Função para atualizar os valores no dashboard
def atualizar_dashboard(temperatura, umidade):
    # Aqui você deve fazer uma solicitação POST para o Flask para atualizar os valores do sensor
    # Use a rota apropriada do Flask para isso

    # Exemplo de como você pode fazer isso:
    data = {'temperatura': temperatura, 'umidade': umidade}
    response = requests.post('http://localhost:5000/api/sensor_data', json=data)

    if response.status_code == 200:
        print('Dados do sensor enviados com sucesso para o servidor Flask local')
    else:
        print('Erro ao enviar dados do sensor para o servidor Flask local')

# Simule dados do sensor
while True:
    temperatura = random.uniform(18, 30)
    umidade = random.uniform(40, 70)

    # Chame a função para atualizar o dashboard com os novos valores
    atualizar_dashboard(temperatura, umidade)

    # Aguarde um intervalo antes de enviar novamente (por exemplo, a cada 10 segundos)
    time.sleep(10)
