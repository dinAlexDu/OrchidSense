import requests
import random
import time
from datetime import datetime

while True:
    temperatura = random.uniform(10, 40)
    humidade = random.uniform(40, 80)

    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sensor_data = {
        'data_hora': data_hora,
        'temperatura': temperatura,
        'humidade': humidade
    }

    response = requests.post('http://localhost:5000/api/sensor_data', json=sensor_data)

    if response.status_code == 200:
        print('Dados do simulador DHT22 enviados com sucesso para o servidor')
    else:
        print('Erro ao enviar dados do simulador DHT22 para o servidor')

    time.sleep(20)
