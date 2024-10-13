import requests
import random
import time
from datetime import datetime

while True:
    luminosidade = random.uniform(0, 3000)  # lux
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sensor_data = {
        'data_hora': data_hora,
        'luminosidade': luminosidade
    }

    response = requests.post('http://localhost:5000/api/sensor_lux_data', json=sensor_data)

    if response.status_code == 200:
        print('Dados de luminosidade enviados com sucesso para o servidor Flask local')
    else:
        print('Erro ao enviar dados de luminosidade para o servidor Flask local')

    time.sleep(20)
