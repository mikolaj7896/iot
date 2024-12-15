import ssl
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt

DEV = False

# Konfiguracja MQTT
MQTT_USERNAME = "python-client"
MQTT_PASSWORD = "admin123"
MQTT_BROKER = "y27feb91.ala.eu-central-1.emqxsl.com"
MQTT_PORT = 8883
MQTT_TOPIC = "temperature"
CLIENT_ID = "mqtt_python_data_collector"

# Konfiguracja InfluxDB
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = "vx9-n5W2ZxrCsOdsyL3R-hnKqBgLcaBgM0dNlyrqUZR5SN4_z3wklaqi3H4GsxyUMoaVvR-r-ZKSELXc2nZ0PA=="
INFLUXDB_ORG = "test"
INFLUXDB_BUCKET = "mqtt_data"

# Połączenie z InfluxDB
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Funkcja przetwarzająca wiadomości MQTT
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode()
        # Sprawdź, czy wiadomość to liczba
        temperature = float(payload) if payload.replace('.', '', 1).isdigit() else None
        print(temperature)
        if temperature is not None:
            print(f"Received temperature: {temperature}")
            # Zapis do InfluxDB
            point = Point("test_topic").field("value", temperature)
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point, write_precision=WritePrecision.NS)
        else:
            print(f"Ignored non-numeric message: '{payload}'")
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    # Konfiguracja klienta MQTT
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Konfiguracja SSL/TLS
    client.tls_set(ca_certs="/cert.crt")

    # Podłącz funkcję obsługi wiadomości
    client.on_message = on_message

    # Połącz z brokerem
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        print("Connected to MQTT broker")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return

    # Subskrybuj temat
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to topic: {MQTT_TOPIC}")

    # Start loop
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        client.disconnect()

main()