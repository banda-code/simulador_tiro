import serial
import time
import requests  # para mandar el disparo al Flask

# Cambia COM3 por el puerto de tu Arduino
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
time.sleep(2)  # Esperar a que Arduino reinicie

while True:
    if arduino.in_waiting > 0:
        data = arduino.readline().decode().strip()
        if data == "DISPARO":
            # Aquí puedes mandar a tu Flask que se registró un disparo
            requests.post("http://127.0.0.1:5000/registrar_disparo",
                          json={"x": 300, "y": 300, "puntos": 10})
            print("Disparo registrado!")
