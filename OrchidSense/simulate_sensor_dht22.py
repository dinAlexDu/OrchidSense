import requests
import random
import time
from datetime import datetime

# Infinite loop to continuously simulate sensor data (temperature and humidity) and send it to the server.
while True:
    # Simulate temperature value (in °C) between 10 and 40.
    temperatura = random.uniform(15, 30)

    # Simulate humidity value (in %) between 40 and 80.
    humidade = random.uniform(40, 80)

    # Get the current date and time in the format 'YYYY-MM-DD HH:MM:SS'.
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create a dictionary with the simulated sensor data.
    sensor_data = {
        'data_hora': data_hora,  # The current timestamp.
        'temperatura': temperatura,  # The simulated temperature value.
        'humidade': humidade  # The simulated humidity value.
    }

    # Send a POST request with the sensor data as JSON to the server's API endpoint.
    response = requests.post('http://localhost:5000/api/sensor_data', json=sensor_data)

    # Check if the data was successfully sent (status code 200 means success).
    if response.status_code == 200:
        print('Dados do simulador DHT22 enviados com sucesso para o servidor')  # Success message
    else:
        print('Erro ao enviar dados do simulador DHT22 para o servidor')  # Error message

    # Wait for 20 seconds before sending the next set of data.
    time.sleep(20)
