import cv2
import numpy as np
import serial
import time
import requests

# Configura el puerto serial para Arduino
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
time.sleep(2)  # Espera que Arduino reinicie

# URL backend Flask
backend_url = "http://127.0.0.1:5000/registrar_disparo"

# Inicializa cámara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

# Tamaño canvas en frontend
canvas_width = 600
canvas_height = 600

# Parámetros opcionales para offset (ajusta si el punto no está centrado)
offset_x = 0
offset_y = 0

def detectar_punto_rojo(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contornos:
        c = max(contornos, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy
    return None

offset_x = -30  # Ajusta estos valores
offset_y = 10

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error leyendo frame")
        break

    punto = detectar_punto_rojo(frame)

    if punto:
        x, y = punto
        cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        x_canvas = int(x * canvas_width / cam_width) + offset_x
        y_canvas = int(y * canvas_height / cam_height) + offset_y

        x_canvas = max(0, min(canvas_width, x_canvas))
        y_canvas = max(0, min(canvas_height, y_canvas))

        dx = x_canvas - canvas_width // 2
        dy = y_canvas - canvas_height // 2
        distancia = (dx**2 + dy**2)**0.5
        if distancia <= 20:
            puntos = 10
        elif distancia <= 50:
            puntos = 7
        elif distancia <= 100:
            puntos = 5
        elif distancia <= 200:
            puntos = 1
        else:
            puntos = 0

        # Mostrar círculo verde en cámara donde detecta el láser
        cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)

        print(f"x_canvas: {x_canvas}, y_canvas: {y_canvas}, puntos: {puntos}")

        if arduino.in_waiting > 0:
            data = arduino.readline().decode().strip()
            if data == "DISPARO":
                requests.post(backend_url,
                              json={"x": x_canvas, "y": y_canvas, "puntos": puntos})
                print(f"Disparo registrado en ({x_canvas}, {y_canvas}) con {puntos} puntos")

    cv2.imshow('Camara', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
