from faster_whisper import WhisperModel
from recorder import record_audio, normalize_audio, save_audio_to_file, process_audio
from mqtt_client import send_mqtt_message  # Import funkcji MQTT
import numpy as np
import time
import torch

DEV = False

# plik z certyfikatem SSL do brokera MQTT musi
# nazywac sie MQTTcert.crt

# Inicjalizacja modelu Whisper
print("Ładowanie modelu Whisper...")
## small 2gb GPU RAM
## medium 5gb GPU RAM
## large 10gb GPU RAM
## turbo 6gb GPU RAM
model_size = "small"

if torch.cuda.is_available():
    device = "cuda"  # Użyj CUDA, jeśli jest dostępne
    print("CUDA dostępne, model zostanie załadowany na GPU.")
else:
    device = "cpu"  # Domyślnie CPU, jeśli CUDA nie jest dostępne
    print("CUDA niedostępne, model zostanie załadowany na CPU.")

model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")

# Parametry nagrania i MQTT
chunk_duration = 5  # Czas trwania chunków w sekundach
total_duration = 360  # Całkowity czas działania programu w sekundach
broker_address = "y27feb91.ala.eu-central-1.emqxsl.com"  # Adres brokera MQTT (zmień na odpowiedni adres)
topic = "whisper"  # Temat MQTT
username = "whisper"  # Użytkownik do logowania
password = "admin123"  # Hasło użytkownika

ca_certs = "C:\\Users\\xevos\\OneDrive\\Pulpit\\iot\\python_subscriber\\cert.crt"  # Ścieżka do certyfikatu SSL 


start_time = time.time()  # Start odliczania czasu

# Funkcja zamienia polskie znaki specjalne na ich odpowiedniki 
# w alfabecie łacińskim

def remove_polish_characters(text):
    '''
        Funkcja zamienia polskie znaki specjalne na ich odpowiedniki 
        w alfabecie łacińskim. Zeby mogly byc poprawnie wyswietlanie na
        za pomoca plytki Node MCU v3
    '''
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ż': 'Z', 'Ź': 'Z'
    }
    return ''.join(replacements.get(c, c) for c in text)

temp_filename = "temp_chunk.wav"  # Jeden plik tymczasowy

while (time.time() - start_time) < total_duration:
    #print("Rozpoczynam nagrywanie chunka...")

    # Nagrywanie i przetwarzanie audio
    audio_data = record_audio(chunk_duration)
    #audio_data = normalize_audio(audio_data)
    #process_audio(audio_data)

    # Zapis do pliku tymczasowego
    save_audio_to_file(audio_data, temp_filename)

    # Transkrypcja nagranego chunku
    segments, info = model.transcribe(temp_filename, word_timestamps=True)

    # Wyświetlanie wykrytego języka i pewności
    #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    # Wysyłanie segmentów transkrypcji jako wiadomości MQTT
    for segment in segments:
        for word in segment.words:
            message = word.word
            print("Nowe słowo: ", message)
            message = remove_polish_characters(message)
            send_mqtt_message(broker_address, topic, message, username, password, ca_certs)

print("Program zakończył nagrywanie i transkrypcję.")