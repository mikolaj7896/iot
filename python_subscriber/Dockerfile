# Plik Dockerfile dla usługi python_app
FROM python:3.11-slim

# Zainstaluj zależności
RUN pip install paho-mqtt influxdb-client

COPY pythonapp.py /pythonapp.py
COPY cert.crt /cert.crt
RUN chmod 777 /cert.crt

ENTRYPOINT ["python", "pythonapp.py"]