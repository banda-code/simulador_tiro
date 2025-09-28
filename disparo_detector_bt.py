# disparo_detector_bt.py
import cv2
import numpy as np
import serial
import time
import requests

# ----- CONFIG -----
BT_COM = 'COM5'                  # <- pon aquí el COM creado por Windows al emparejar HC-05
BT_BAUD = 9600
CAM_URL = "http://10.36.205.181:8080/video"  # <- URL que te da IP Webcam (ajusta IP
# CAM_URL = "http://10.79.228.236:8080/video"  # <- URL que te da IP Webcam (ajusta IP)
# CAM_URL = "http://192.168.74.35:8080/video"  # <- URL que te da IP Webcam (ajusta IP)

BACKEND_URL = "http://127.0.0.1:5000/registrar_disparo"
CANVAS_W, CANVAS_H = 500, 500
OFFSET_X = 0
OFFSET_Y = 0
# -------------------

# Conectar Bluetooth serial (HC-05)
try:
    arduino = serial.Serial(BT_COM, BT_BAUD, timeout=1)
    time.sleep(2)
    print(f"Conectado a {BT_COM}")
except Exception as e:
    print("Error abriendo puerto serial Bluetooth:", e)
    arduino = None

# Abrir stream de la cámara del celular
cap = cv2.VideoCapture(CAM_URL)  # o 0 para webcam integrada
if not cap.isOpened():
    print("No se pudo abrir el stream de la cámara.")
    cap = cv2.VideoCapture(0)  # fallback

def detectar_punto_rojo(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0, 150, 150])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([160, 150, 150])
    upper2 = np.array([179, 255, 255])
    mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=2)
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contornos:
        c = max(contornos, key=cv2.contourArea)
        ((x, y), r) = cv2.minEnclosingCircle(c)
        if r > 3:
            return int(x), int(y), int(r)
    return None, None, None

while True:
    ret, frame = cap.read()
    if not ret:
        print("No frame")
        break

    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or frame.shape[1]
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or frame.shape[0]

    x, y, r = detectar_punto_rojo(frame)
    # Depuración: imprime coordenadas
    # if x is not None:
        # print(f"Láser detectado en: {x}, {y}, radio: {r}")
    # else:
        # print("Láser no detectado en este frame")
    if x is not None:
        # Mapea coords cámara -> canvas
        x_canvas = int(x * CANVAS_W / cam_w) + OFFSET_X
        y_canvas = int(y * CANVAS_H / cam_h) + OFFSET_Y
        x_canvas = max(0, min(CANVAS_W, x_canvas))
        y_canvas = max(0, min(CANVAS_H, y_canvas))
        


        cv2.circle(frame, (x, y), r, (0,255,0), 2)
        cv2.putText(frame, f"({x},{y}) -> ({x_canvas},{y_canvas})", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    else:
        cv2.putText(frame, "No detectado", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # Leer señal Bluetooth (HC-05)
    if arduino and arduino.in_waiting:
        line = arduino.readline().decode().strip()
        print("BT>", line)
        if line == "DISPARO":
            if x is not None:
                # Calcular puntos por distancia al centro (opcional)
                dx = x_canvas - CANVAS_W//2
                dy = y_canvas - CANVAS_H//2
                dist = (dx*dx + dy*dy)**0.5
                if dist <= 20: puntos = 10
                elif dist <= 50: puntos = 7
                elif dist <= 100: puntos = 5
                elif dist <= 200: puntos = 1
                else: puntos = 0

                # Enviar al backend (Flask)
                try:
                    r = requests.post(BACKEND_URL, json={"x": x_canvas, "y": y_canvas, "puntos": puntos}, timeout=2)
                    print("Enviado al backend:", r.status_code)
                except Exception as e:
                    print("Error al enviar:", e)
            else:
                print("DISPARO pero no detectado el láser en frame")

    cv2.imshow("Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if arduino: arduino.close()
