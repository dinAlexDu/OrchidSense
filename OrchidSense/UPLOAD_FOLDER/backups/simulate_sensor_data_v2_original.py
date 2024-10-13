import requests
import random
import time

# Simule dados do sensor
while True:
    temperatura = random.uniform(18, 30)
    humidade = random.uniform(40, 70)

    # Crie um dicionário com os dados simulados
    sensor_data = {'temperatura': temperatura, 'humidade': humidade}

    # Envie os dados para a rota da API no servidor Flask local
    response = requests.post('http://localhost:5000/api/sensor_data', json=sensor_data)

    if response.status_code == 200:
        print('Dados do sensor enviados com sucesso para o servidor Flask local')
    else:
        print('Erro ao enviar dados do sensor para o servidor Flask local')

    # Aguarde um intervalo antes de enviar novamente (por exemplo, a cada 10 segundos)
    time.sleep(3)
