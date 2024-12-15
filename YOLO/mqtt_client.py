import paho.mqtt.client as mqtt

def send_mqtt_message(broker_address, topic, message, username, password, ca_certs):
    """
    Łączy się z brokerem MQTT z uwierzytelnianiem i SSL i wysyła wiadomość na wskazany temat.
    
    :param broker_address: Adres IP lub URL brokera MQTT
    :param topic: Temat, na który wiadomość ma być wysłana
    :param message: Treść wiadomości
    :param username: Nazwa użytkownika do logowania
    :param password: Hasło użytkownika do logowania
    :param ca_certs: Ścieżka do pliku certyfikatu SSL
    """
    # Tworzymy klienta MQTT
    client = mqtt.Client()

    # Konfiguracja uwierzytelniania
    client.username_pw_set(username, password)

    # Konfiguracja SSL z certyfikatem
    client.tls_set(ca_certs=ca_certs)

    # Łączymy się z brokerem
    try:
        client.connect(broker_address, port=8883)  # port 8883 dla SSL
        # Publikujemy wiadomość na temat
        client.publish(topic, message)
        #print(f"Wysłano wiadomość na temat '{topic}': {message}")
    except Exception as e:
        print(f"Nie udało się połączyć z brokerem MQTT: {e}")
    finally:
        # Zakończ połączenie
        client.disconnect()