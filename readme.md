# Real Time DS18B20 temp sensor, Whisper and YOLOv8 object recognition on NodeMCU v3
## Desciption
It uses Open AI Whisper model by recording 5 second chunks from default audio input device, prints recognized speech on LCD screen connected to the NodeMCU v3 board. Works with both CPU and CUDA, but CUDA is a lot faster.

## Hardware requirements
- NodeMCU v3 board
- DS18B20 temperature sensor
- Preferably PC / Laptop with NVidia GPU

## Software requirements
- Python 3.11
- libraries from requirements.txt
- SSL cert for MQTT connection in \\python_subscriber\\cert.crt

## CUDA Requirements
- CUDA 12.4 (12.6 doesnt work with torch)

## Run Whisper / YOLO
- int terminal navigate into folder whisper_realtime / YOLO
- type Scripts\Activate.ps1 for venv
- type python .\main.py
