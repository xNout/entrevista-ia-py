# core/voice_capture.py

import sounddevice as sd
import numpy as np
import librosa
import tempfile
import scipy.io.wavfile
from sklearn.preprocessing import StandardScaler
import speech_recognition as sr
from sklearn.neighbors import KNeighborsClassifier

SAMPLE_RATE = 22050
CHANNELS = 1

class VoiceRecorder:
    def __init__(self):
        self.frames = []
        self.stream = None
        self.temp_file = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"⚠️ Error de grabación: {status}")
        self.frames.append(indata.copy())

    def start_recording(self):
        print("🎙️ Grabando voz (tiempo indefinido)...")
        self.frames = []
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='float32',
            callback=self._callback
        )
        self.stream.start()

    def stop_recording_and_analyze(self):
        print("🛑 Deteniendo grabación de voz...")
        self.stream.stop()
        self.stream.close()

        # Unir todos los frames grabados
        audio_data = np.concatenate(self.frames, axis=0)

        # Guardar como WAV válido (PCM int16)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            self.temp_file = tmpfile.name
            int_audio = np.int16(audio_data * 32767)
            scipy.io.wavfile.write(tmpfile.name, SAMPLE_RATE, int_audio)
            print(f"🎧 Archivo guardado: {self.temp_file}")

        emocion = self._analizar_emocion()
        texto = self._transcribir_audio()
        return emocion, texto

    def _analizar_emocion(self):
        audio, sr = librosa.load(self.temp_file, sr=SAMPLE_RATE)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features = np.mean(mfccs.T, axis=0).reshape(1, -1)

        emotions = ['calmado', 'feliz', 'enojado']
        mock_X = np.array([np.random.rand(13) for _ in emotions])
        mock_y = emotions

        scaler = StandardScaler()
        clf = KNeighborsClassifier(n_neighbors=1)
        clf.fit(scaler.fit_transform(mock_X), mock_y)

        return clf.predict(scaler.transform(features))[0]

    def _transcribir_audio(self):
        print("🔠 Transcribiendo respuesta...")
        recognizer = sr.Recognizer()
        with sr.AudioFile(self.temp_file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES")
            print(f"📝 Transcripción: {texto}")
            return texto
        except sr.UnknownValueError:
            print("🤷 No se pudo entender el audio.")
            return "[Ininteligible]"
        except sr.RequestError:
            print("⚠️ Error al conectar con el servicio de reconocimiento.")
            return "[Error de reconocimiento]"
