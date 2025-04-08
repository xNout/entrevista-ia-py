import cv2
from deepface import DeepFace
import threading
import time

class EmotionRecorder:
    def __init__(self):
        self.frames = []
        self.running = False
        self.cap = None
        self.thread = None

    def start(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("⚠️ No se pudo acceder a la cámara.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()
        print("🎥 Cámara iniciada...")

    def _record(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frames.append(frame)
            time.sleep(0.1)  # ~10 fps

    def stop(self):
        self.running = False
        time.sleep(0.5)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("📷 Cámara detenida. Analizando emociones...")

    def analizar_emocion(self):
        emociones_detectadas = []

        traducciones = {
            "angry": "enojado",
            "disgust": "disgustado",
            "fear": "miedo",
            "happy": "feliz",
            "sad": "triste",
            "surprise": "sorprendido",
            "neutral": "neutral"
        }

        for frame in self.frames:
            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                emocion = result[0]['dominant_emotion']
                emociones_detectadas.append(emocion)
            except Exception:
                continue

        if emociones_detectadas:
            dominante = max(set(emociones_detectadas), key=emociones_detectadas.count)
            return traducciones.get(dominante, dominante)  # traducir si existe
        else:
            return "no_detectado"

