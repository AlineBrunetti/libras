import json
import random
import time
from collections import Counter, deque
import cv2
import numpy as np
import tensorflow as tf

IMG_SIZE = 224
class_names = json.load(open("class_names.json"))

# Carrega o modelo convertido para TFLite (MUITO mais leve)
interpreter = tf.lite.Interpreter(model_path="gesture_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict(roi):
    img = cv2.cvtColor(cv2.resize(roi, (IMG_SIZE, IMG_SIZE)), cv2.COLOR_BGR2RGB)
    
    # Roda a imagem pelo TFLite em vez de usar o modelo Keras completo
    interpreter.set_tensor(input_details[0]['index'], img[None].astype("float32"))
    interpreter.invoke()
    probs = interpreter.get_tensor(output_details[0]['index'])[0]
    
    return class_names[int(np.argmax(probs))], float(np.max(probs)), probs

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Nao consegui abrir a webcam.")
    
recent = deque(maxlen=7)          

# Variáveis para guardar o último resultado (para quando pulamos frames)
stable = "Aguardando..."
conf = 0.0
probs = np.zeros(len(class_names))
frame_count = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    side = min(h, w) // 2 + 60
    x1, y1 = w // 2 - side // 2, h // 2 - side // 2
    roi = frame[y1:y1 + side, x1:x1 + side]
    
            # Agora que usamos TFLite que é muito leve, podemos analisar a cada 3 frames de novo
    if frame_count % 3 == 0:
        label, conf, probs = predict(roi)
        recent.append(label)
        stable = Counter(recent).most_common(1)[0][0]
    frame_count += 1

            # Retângulo de foco em Preto
    cv2.rectangle(frame, (x1, y1), (x1 + side, y1 + side), (0, 0, 0), 3)
    
    # Texto de "Sinal:" em Preto
    cv2.putText(frame, f"Sinal: {stable} ({conf:.0%})", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                
    for i, c in enumerate(class_names):
        bw = int(probs[i] * 150)
        # Barra da porcentagem em Preto
        cv2.rectangle(frame, (10, 50 + i * 22), (10 + bw, 64 + i * 22), (0, 0, 0), -1)
        # Letras da classe em Preto
        cv2.putText(frame, c, (170, 63 + i * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
    cv2.imshow("Reconhecimento de Libras com CNN", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
