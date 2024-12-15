import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time

# Parametry domyślne
SAMPLE_RATE = 48000  # Ustawione na 48 kHz zgodnie z mikrofonem
CHANNELS = 2  # Zgodne z ustawieniami mikrofonu

def record_audio(duration: int):
    """
    Nagrywa audio przez określoną liczbę sekund i zwraca nagranie.
    
    duration: Czas nagrania w sekundach
    :return: Zwraca nagranie audio jako tablicę numpy
    """
    recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
    sd.wait()  # Czekaj na zakończenie nagrania
    print("Nagrywanie zakończone.")
    return recording

def play_audio(audio_data: np.ndarray):
    """
    Odtwarza nagrane audio.
    
    audio_data: Nagranie audio w postaci tablicy numpy
    """
    print("Odtwarzanie nagrania...")
    sd.play(audio_data, samplerate=SAMPLE_RATE)
    sd.wait()  # Czekaj na zakończenie odtwarzania
    print("Odtwarzanie zakończone.")

def normalize_audio(audio_data: np.ndarray, target_amplitude=0.8):
    """
    Normalizuje nagranie audio do określonego poziomu amplitudy.
    Aktualnie wylaczona, bo nie dziala zbyt dobrze
    
    audio_data: Tablica numpy z danymi audio
    target_amplitude: Docelowa maksymalna wartość amplitudy (domyślnie 0.9)
    :return: Zwraca znormalizowane dane audio
    """
    max_amplitude = np.max(np.abs(audio_data))
    normalized_audio = (audio_data / max_amplitude) * target_amplitude
    #print(f"Audio znormalizowane do poziomu {target_amplitude}")
    return normalized_audio

def save_audio_to_file(audio_data: np.ndarray, filename: str):
    """
    Zapisuje nagranie audio do pliku .wav.
    
    audio_data: Tablica numpy z danymi audio
    filename: Nazwa pliku do zapisu
    """
    scaled_audio = np.int16(audio_data * 32767)
    write(filename, SAMPLE_RATE, scaled_audio)
    #print(f"Nagranie zapisane do pliku {filename}")

def process_audio(audio_data: np.ndarray):
    """
    audio_data: Tablica numpy z danymi audio

    tu beda funkcje do nasluchiwania na komendy
    """
    #print(f"Długość nagrania: {len(audio_data) / SAMPLE_RATE:.2f} s")
    #print(f"Maksymalna amplituda: {np.max(np.abs(audio_data)):.2f}")

# Przykład użycia
if __name__ == "__main__":
    '''
    Funkcja main do sprawdzania urzadzen audio i wybrania wlasciwego
    nagrywa dzwiek zadanym urzadzeniem wybranym z listy dostepnych urzadzen
    zapisuje plik w celu weryfikacji czy mikrofon nagrywa
    
    '''
    try:
        print("Dostępne urządzenia input audio: ", sd.query_devices())
        duration = int(input("Podaj czas nagrywania (w sekundach): "))
        audio_data = record_audio(duration)
        print("Audio nagrane pomyślnie.")
        
        # Zapis do pliku WAV
        timestamp = int(time.time())  # Użycie znacznika czasu dla unikalnej nazwy pliku
        filename = f"mic_test.wav"
        save_audio_to_file(audio_data, filename)
    except Exception as e:
        print(f"Błąd: {e}")