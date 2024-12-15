import cv2
from ultralytics import YOLO
import mqtt_client
import time

# Konfiguracja MQTT
BROKER_ADDRESS = "y27feb91.ala.eu-central-1.emqxsl.com"  # Adres brokera MQTT
TOPIC = "object_recognition"
USERNAME = "yolo"
PASSWORD = "admin123"

CA_CERTS = "C:\\Users\\xevos\\OneDrive\\Pulpit\\iot\\python_subscriber\\cert.crt"  # Ścieżka do certyfikatu SSL

# Inicjalizacja modelu YOLOv8
model = YOLO("yolov8s.pt")  # Wybór modelu YOLOv8 (np. n=Nano, s=Small itp.)

# Funkcja do wysyłania nazw obiektów przez MQTT
def send_detected_objects(detected_objects):
    for obj in detected_objects:
        try:
            mqtt_client.send_mqtt_message(
                broker_address=BROKER_ADDRESS,
                topic=TOPIC,
                message=obj,
                username=USERNAME,
                password=PASSWORD,
                ca_certs=CA_CERTS,
            )
        except Exception as e:
            print(f"Błąd podczas wysyłania wiadomości MQTT: {e}")

# Tryb z podglądem w GUI (dla DEV=True)
def debug_mode():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można otworzyć kamerki.")
        exit()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Nie udało się odczytać klatki z kamerki.")
                break

            # Wykrywanie obiektów
            results = model(frame)
            detected_objects = set()

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    object_name = model.names[class_id]
                    detected_objects.add(object_name)

            # Wysyłanie wyników przez MQTT
            send_detected_objects(detected_objects)

            # Wyświetlanie klatek z zaznaczeniami
            annotated_frame = results[0].plot()
            cv2.imshow("YOLOv8 Object Detection", annotated_frame)

            # Wyjście po naciśnięciu 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Przerwano działanie programu.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

# Tryb headless (dla DEV=False)
def headless_mode():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można otworzyć kamerki.")
        exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(
        "output.avi",
        cv2.VideoWriter_fourcc(*"XVID"),
        10,
        (frame_width, frame_height)
    )

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Nie udało się odczytać klatki z kamerki.")
                break

            # Wykrywanie obiektów
            results = model(frame)
            detected_objects = set()

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    object_name = model.names[class_id]
                    detected_objects.add(object_name)

            # Wysyłanie wyników przez MQTT
            send_detected_objects(detected_objects)

            # Zapis klatek z zaznaczeniami
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

            # Opóźnienie (np. 1 sekunda)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Przerwano działanie programu.")
    finally:
        cap.release()
        out.release()
        print("Zamknięto strumień wideo.")

debug_mode()