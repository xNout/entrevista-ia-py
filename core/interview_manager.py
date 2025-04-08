import pyttsx3

# Inicializar el motor
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

# Seleccionar voz en español si está instalada
for voice in engine.getProperty("voices"):
    if "spanish" in voice.name.lower():
        engine.setProperty("voice", voice.id)

PREGUNTAS_BÁSICAS = [
    "¿Cuál es tu nombre completo?",
    "¿Cuántos años tienes?",
    "¿Dónde resides actualmente?",
    "¿En qué empresa estás trabajando ahora?",
    "¿Cuál es tu disponibilidad para comenzar?",
    "¿Por qué estás interesado en este puesto?"
]

def hablar(texto: str):
    print(f"[IA] {texto}")
    engine.say(texto)
    engine.runAndWait()
