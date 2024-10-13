# OrchidSense - Web App for Monitoring Environmental Conditions

## Overview

OrchidSense is a web application that monitors environmental conditions such as temperature, humidity, and light levels using IoT technologies. This project is particularly aimed at orchid growers who require precise control over their plant environments. The system is based on Raspberry Pi with DHT22 and BH1750 sensors and provides real-time data visualization, historical analysis, and alert notifications when conditions deviate from optimal ranges.

## Features

- **Real-Time Monitoring:** Data from the DHT22 (temperature, humidity) and BH1750 (light intensity) sensors is displayed in real-time.
- **Historical Data Analysis:** Users can analyze environmental conditions over hourly, daily, weekly, and monthly intervals through graphs and tables.
- **Alert System:** Users can configure alerts based on predefined environmental thresholds. Notifications are sent via email when conditions fall outside the optimal ranges.
- **Orchid Library:** A collection of common orchid species with details about their ideal environmental conditions.
- **Responsive Design:** The web app is accessible from any device, with an intuitive and modern user interface.
- **User Authentication:** Secure user registration and login with role-based access control for administrators.

## Technologies Used

- **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript
- **Backend:** Python (Flask)
- **Database:** MySQL
- **Hardware:** Raspberry Pi, DHT22 (temperature and humidity sensor), BH1750 (light sensor)
- **Other:** Flask-Login for authentication, Flask-Mail for email notifications

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/orchidsense.git
    ```

2. Set up the virtual environment and install dependencies:
    ```bash
    cd orchidsense
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Set up the MySQL database and apply migrations:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

4. Configure the `.env` file with your database and mail server credentials.

5. Run the application:
    ```bash
    flask run
    ```

## Screenshots

### Login Page
![Login](static/assets/screenshots/login.png)

### Dashboard - Real-Time Data Monitoring
![Real-Time Data](static/assets/screenshots/dados_em_tempo_real.png)

### Graphs of Temperature and Humidity Over Time
![Graphs - Temperature and Humidity](static/assets/screenshots/dados_em_tempo_real_graficos_temp_hum.png)

### Graphs of Light Intensity Over Time
![Graphs - Light Intensity](static/assets/screenshots/dados_em_tempo_real_graficos_lux.png)

### Analysis and Reports - Main Page
![Reports Main Page](static/assets/screenshots/analises_e_relatorios_main.png)

### Hourly Graph for Environmental Data
![Hourly Graph](static/assets/screenshots/analises_e_relatorios_grafico_horario.png)

### Export Reports
![Export Reports](static/assets/screenshots/analises_e_relatorios_export.png)

### Orchid Library
![Orchid Library](static/assets/screenshotss/biblioteca_de_orquideas.png)

### Alerts and Notifications - List View
![List of Alerts](static/assets/screenshots/alertas_e_notificacoes_list.png)

### Alerts and Notifications - Add Configuration
![Add Alert Configuration](path-to-screenshots/alertas_e_notificacoes_add_config.png)

### Alerts and Notifications - Edit Configuration
![Edit Alert Configuration](static/assets/screenshots/alertas_e_notificacoes_edit.png)


### Device Management
![Device Management](static/assets/screenshots/gestao_de_dispositivos.png)

### User List
![User List](static/assets/screenshots/gestao_de_utilizadores_list.png)

### Add New User
![Add User](static/assets/screenshots/gestao_de_utilizadores_add_user.png)

### Edit User Information
![Edit User](static/assets/screenshots/gestao_de_utilizadores_edit_user.png)



## Hardware Setup

The system uses a **Raspberry Pi** to interface with the DHT22 and BH1750 sensors. Below is an image showing the hardware setup.

### Hardware Connection

![Hardware Setup](path-to-hardware-image/hardware.jpg)

This image shows the Raspberry Pi connected to the sensors (DHT22 and BH1750) using a breadboard and jumper wires.

### Components Used:
- **Raspberry Pi**: Acts as the main control unit, running the Flask web server and interfacing with sensors.
- **DHT22**: Sensor for temperature and humidity.
- **BH1750**: Sensor for light intensity (lux).
- **Breadboard and Jumper Wires**: Used for prototyping and connecting sensors to the Raspberry Pi GPIO pins.

## Usage

Once the application is up and running, users can log in to view their dashboard, set up alerts, and explore the orchid library. The real-time data is pulled from the sensors and displayed in graphical form. Historical data can be reviewed for deeper analysis, and alerts notify users if conditions go out of range.

## Contributors

- **Dinis Duarte** - Lead Developer and Project Manager

## License

This project is licensed under the MIT License.
