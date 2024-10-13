import requests
import random
import time
from datetime import datetime

# Infinite loop to continuously simulate sensor data and send it to the server.
while True:
    # Simulate the luminosity value (lux) with a random number between 0 and 50,000.
    luminosidade = random.uniform(0, 50000)  # lux (light intensity)

    # Get the current date and time in the format 'YYYY-MM-DD HH:MM:SS'.
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create a dictionary with the simulated sensor data.
    sensor_data = {
        'data_hora': data_hora,  # The current timestamp.
        'luminosidade': luminosidade  # The simulated luminosity value.
    }

    # Send a POST request with the sensor data as JSON to the server's API endpoint.
    response = requests.post('http://localhost:5000/api/sensor_lux_data', json=sensor_data)

    # Check if the data was successfully sent (status code 200 means success).
    if response.status_code == 200:
        print('Dados do simulador bh1750 enviados com sucesso para o servidor')  # Success message
    else:
        print('Erro ao enviar dados do simulador BH1750 para o servidor')  # Error message

    # Wait for 20 seconds before sending the next set of data.
    time.sleep(20)


