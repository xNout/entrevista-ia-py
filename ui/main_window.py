import customtkinter as ctk
from tkinter import messagebox
from core.interview_manager import PREGUNTAS_BÁSICAS, hablar
from core.voice_capture import VoiceRecorder
from utils.styles import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, PRIMARY_COLOR
from core.emotion_capture import EmotionRecorder
import json
from tkinter import filedialog
import datetime
import csv
import zipfile
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        # Tamaño de ventana
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

                # Tamaño deseado
        width = WINDOW_WIDTH
        height = WINDOW_HEIGHT

        # Obtener dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calcular posición centrada
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Aplicar tamaño y posición final
        self.geometry(f"{width}x{height}+{x}+{y}")


        self.resizable(False, False)

        self.pregunta_index = 0
        self.estado_entrevista = "preguntar"  # puede ser: preguntar, esperando_respuesta, guardando
        self.respuestas = []  # Cada ítem será: {'pregunta': ..., 'respuesta_texto': ..., 'emocion_facial': ..., 'emocion_vocal': ...}

        
        # Cerrar ventana
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Widgets
        self.title_label = ctk.CTkLabel(self, text="Sistema de Entrevistas con IA", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=20)

        self.pregunta_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18), wraplength=500, justify="center")
        self.pregunta_label.pack(pady=20)

        # self.input_entry = ctk.CTkEntry(self, width=400)
        # self.input_entry.pack(pady=10)

        self.next_button = ctk.CTkButton(self, text="Iniciar Entrevista", command=self.on_boton_principal_click)
        self.next_button.pack(pady=20)

        self.footer = ctk.CTkLabel(self, text="Versión prototipo - 2025", font=ctk.CTkFont(size=12))
        self.footer.pack(side="bottom", pady=10)

    def on_boton_principal_click(self):
        if self.estado_entrevista == "preguntar":
            self.mostrar_pregunta()
        elif self.estado_entrevista == "esperando_respuesta":
            self.iniciar_respuesta()
        elif self.estado_entrevista == "guardando":
            self.guardar_respuesta()

    def mostrar_pregunta(self):
        if self.pregunta_index >= len(PREGUNTAS_BÁSICAS):
            self.finalizar_entrevista()
            return

        pregunta_actual = PREGUNTAS_BÁSICAS[self.pregunta_index]
        self.pregunta_label.configure(text=pregunta_actual)

        from core.interview_manager import hablar
        self.after(100, lambda: hablar(pregunta_actual))

        # Cambiar estado y botón
        self.estado_entrevista = "esperando_respuesta"
        self.next_button.configure(text="Responder", state="normal")

    def iniciar_respuesta(self):
        print("🎥 Iniciando cámara y micrófono...")

        self.emotion_recorder = EmotionRecorder()
        self.voice_recorder = VoiceRecorder()

        self.emotion_recorder.start()
        self.voice_recorder.start_recording()

        self.estado_entrevista = "guardando"
        self.next_button.configure(text="Guardar mi respuesta")


    def guardar_respuesta(self):
        print("💾 Guardando respuesta...")

        # Detener captura facial
        self.emotion_recorder.stop()
        
        # Detener y analizar audio + transcribir
        emocion_vocal, transcripcion = self.voice_recorder.stop_recording_and_analyze()
        print(f"🎧 Emoción vocal: {emocion_vocal}")
        
        # analisis de emocion
        emocion_facial = self.emotion_recorder.analizar_emocion()
        print(f"🙂 Emoción facial detectada: {emocion_facial}")

        

        self.respuestas.append({
            "pregunta": PREGUNTAS_BÁSICAS[self.pregunta_index],
            "respuesta_texto": transcripcion,
            "emocion_facial": emocion_facial,
            "emocion_vocal": emocion_vocal,
        })

        self.pregunta_index += 1
        self.estado_entrevista = "preguntar"
        self.next_button.configure(text="Siguiente", state="disabled")
        self.after(1000, self.mostrar_pregunta)



    def on_close(self):
            # Aquí podemos agregar lógica adicional más adelante
            print("🛑 Cerrando aplicación...")
            self.destroy()  # Cierra ventana
            self.quit()     # Cierra el loop de Tkinter
            import sys
            sys.exit(0)   

    def reproducir_voz(self, texto):
        from core.interview_manager import hablar
        hablar(texto)

    def generar_conclusiones(self):
        emociones_f = [r["emocion_facial"] for r in self.respuestas]
        emociones_v = [r["emocion_vocal"] for r in self.respuestas]

        def emocion_dominante(lista):
            return max(set(lista), key=lista.count) if lista else "no_detectado"

        dominante_facial = emocion_dominante(emociones_f)
        dominante_vocal = emocion_dominante(emociones_v)

        congruentes = sum(1 for f, v in zip(emociones_f, emociones_v) if f == v)
        congruencia = f"{(congruentes / len(self.respuestas)) * 100:.1f}%" if self.respuestas else "0%"

        motivacion_detectada = any(
            "crecimiento" in r["respuesta_texto"].lower() or
            "salario" in r["respuesta_texto"].lower()
            for r in self.respuestas
        )

        tono_general = "positivo" if dominante_vocal == "feliz" else "neutral" if dominante_vocal == "calmado" else "negativo"
        recomendacion = "Candidato potencial con buena actitud." if tono_general == "positivo" else \
                        "Evaluar con más profundidad. Posibles alertas emocionales."

        return {
            "emocion_facial_dominante": dominante_facial,
            "emocion_vocal_dominante": dominante_vocal,
            "congruencia_voz_rostro": congruencia,
            "tono_general": tono_general,
            "motivacion_detectada": motivacion_detectada,
            "recomendacion": recomendacion
        }


    def finalizar_entrevista(self):
        self.pregunta_label.configure(text="¡Entrevista finalizada! Gracias por participar.")
        self.next_button.configure(state="disabled")

        carpeta_destino = filedialog.askdirectory(title="Selecciona una carpeta para guardar el informe")

        if not carpeta_destino:
            print("🚫 No se seleccionó carpeta.")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"entrevista_{timestamp}"
        json_path = os.path.join(carpeta_destino, f"{base_name}.json")
        txt_path = os.path.join(carpeta_destino, f"{base_name}.txt")
        csv_path = os.path.join(carpeta_destino, f"{base_name}.csv")
        zip_path = os.path.join(carpeta_destino, f"{base_name}.zip")

        # --- JSON ---
        data = {
            "candidato": {
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "respuestas": self.respuestas,
                "conclusiones": self.generar_conclusiones()
            }
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # --- TXT ---
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"📝 INFORME DE ENTREVISTA\nFecha: {data['candidato']['fecha']}\n\n")
            for r in self.respuestas:
                f.write(f"❓ {r['pregunta']}\n")
                f.write(f"📣 Respuesta: {r['respuesta_texto']}\n")
                f.write(f"🙂 Emoción facial: {r['emocion_facial']}\n")
                f.write(f"🎧 Emoción vocal: {r['emocion_vocal']}\n")
                f.write("—" * 40 + "\n")

            traducciones = {
                "emocion_facial_dominante": "Emoción facial dominante",
                "emocion_vocal_dominante": "Emoción vocal dominante",
                "congruencia_voz_rostro": "Congruencia voz-rostro",
                "tono_general": "Tono general",
                "motivacion_detectada": "Motivación detectada",
                "recomendacion": "Recomendación"
            }

            for key, value in data["candidato"]["conclusiones"].items():
                etiqueta = traducciones.get(key, key.replace("_", " ").capitalize())
                if isinstance(value, bool):
                    value = "Sí" if value else "No"
                f.write(f"• {etiqueta}: {value}\n")


        # --- CSV ---
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Pregunta", "Respuesta", "Emoción Facial", "Emoción Vocal"])
            for r in self.respuestas:
                writer.writerow([r["pregunta"], r["respuesta_texto"], r["emocion_facial"], r["emocion_vocal"]])

        # --- ZIP ---
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(json_path, os.path.basename(json_path))
            zipf.write(txt_path, os.path.basename(txt_path))
            zipf.write(csv_path, os.path.basename(csv_path))

        # Eliminar archivos individuales si no se necesitan por separado
        os.remove(json_path)
        os.remove(txt_path)
        os.remove(csv_path)

        print(f"✅ Informe generado correctamente en: {zip_path}")
        self.after(2000, self.on_close)

        # Mostrar resumen de conclusiones en consola
        print("\n📊 RESUMEN FINAL PARA REVISIÓN INMEDIATA:")
        conclusiones = data["candidato"]["conclusiones"]
        for clave, valor in conclusiones.items():
            etiqueta = {
                "emocion_facial_dominante": "Emoción facial dominante",
                "emocion_vocal_dominante": "Emoción vocal dominante",
                "congruencia_voz_rostro": "Congruencia voz-rostro",
                "tono_general": "Tono general",
                "motivacion_detectada": "Motivación detectada",
                "recomendacion": "Recomendación"
            }.get(clave, clave.replace("_", " ").capitalize())

            if isinstance(valor, bool):
                valor = "Sí" if valor else "No"

            print(f"• {etiqueta}: {valor}")






def run_main_window():
    app = MainApp()
    app.mainloop()
