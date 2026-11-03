import os
import time
import cv2

KEYS = {
    ord("a"): "A",
    ord("b"): "B",
    ord("c"): "C",
    ord("d"): "D",
    ord("e"): "E",
    ord("f"): "F",
    ord("i"): "I",
    ord("l"): "L",
    ord("o"): "O",
    ord("u"): "U",
    ord("n"): "nada",
}
CLASSES = ["A", "B", "C", "D", "E", "F", "I", "L", "O", "U", "nada"]
DATA_DIR = "data"
IMG_SIZE = 224
SAVE_EVERY_N_FRAMES = 3
MAX_PER_CLASS = 300  # Aumentado para 300 por classe (fundo escuro e claro)
COUNTDOWN = 3.0
DEBOUNCE = 0.5   

for c in CLASSES:
    os.makedirs(os.path.join(DATA_DIR, c), exist_ok=True)

def count(cls):
    return len([f for f in os.listdir(os.path.join(DATA_DIR, cls)) if f.endswith(".jpg")])

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Nao consegui abrir a webcam.")
else:
    recording = None       
    countdown_start = None
    last_key_time = 0
    frame_count = 0
    WIN = "Coleta Libras"
    print("Janela aberta. Clique nela e aperte as letras (a, b, c, d, e, f, i, l, o, u, n). 'q' sai.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Falha ao ler a webcam.")
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        side = min(h, w) // 2 + 60
        x1, y1 = w // 2 - side // 2, h // 2 - side // 2
        roi = frame[y1:y1 + side, x1:x1 + side]

        status, color = "PARADO - aperte a/b/c/d/e/f/i/l/o/u/n", (0, 255, 0)
        
        if recording and countdown_start is not None:
            left = COUNTDOWN - (time.time() - countdown_start)
            if left > 0:
                status, color = f"{recording}: prepare a mao... {int(left) + 1}", (0, 255, 255)
            else:
                countdown_start = None

        if recording and countdown_start is None:
            status, color = f"GRAVANDO: {recording}", (0, 0, 255)
            frame_count += 1
            if frame_count % SAVE_EVERY_N_FRAMES == 0:
                if count(recording) < MAX_PER_CLASS:
                    img = cv2.resize(roi, (IMG_SIZE, IMG_SIZE))
                    cv2.imwrite(os.path.join(DATA_DIR, recording, f"{int(time.time() * 1000)}.jpg"), img)
                else:
                    print(f"{recording}: completo ({MAX_PER_CLASS} fotos).")
                    recording = None

        cv2.rectangle(frame, (x1, y1), (x1 + side, y1 + side), color, 3)
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        for i, c in enumerate(CLASSES):
            cv2.putText(frame, f"[{c[0].lower()}] {c}: {count(c)}/{MAX_PER_CLASS}", (10, 65 + i * 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        
        cv2.imshow(WIN, frame)
        key = cv2.waitKey(10) & 0xFF

        if key == 255:
            continue
        if key == ord("q"):
            break
        if key in KEYS and time.time() - last_key_time > DEBOUNCE:
            last_key_time = time.time()
            cls = KEYS[key]
            if recording == cls:
                recording = None
                print(f"Pausado: {cls}")
            else:
                recording, countdown_start = cls, time.time()
                print(f"Preparando: {cls}")
        elif key not in KEYS:
            print(f"(tecla nao reconhecida: codigo {key})")

    cap.release()
    cv2.destroyAllWindows()
    print({c: count(c) for c in CLASSES})
