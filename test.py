import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Listar voces disponibles
for voice in voices:
    print(f"ID: {voice.id} - Nombre: {voice.name} - Idioma: {voice.languages}")

# Seleccionar la voz en español
engine.setProperty('voice', voices[2].id)
engine.say("Hola, esta es una prueba de voz en español.")
engine.runAndWait()
