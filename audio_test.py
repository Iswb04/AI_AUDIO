import tkinter as tk
from tkinter import ttk
import pyttsx3
import speech_recognition as sr
import threading
import requests
from datetime import datetime
import time
import random
import os
from PIL import Image, ImageTk

# --- CONFIGURAÇÕES ---
WAKE_WORD = "python"
OLLAMA_URL = "http://localhost:11434/api/generate"
IMAGE_DIR = "imagens"

class RobotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Prototype - 128x64 Images")
        self.root.configure(bg="#2c3e50")
        
        self.is_listening = False
        self.engine = pyttsx3.init()
        self.setup_default_voice()
        
        # UI Layout
        self.setup_ui()
        
        # Load Images
        self.load_images()
        
        # Definição dos dígitos pixelados (Matriz 3x5)
        self.pixel_digits = {
            '0': [(0,0), (1,0), (2,0), (0,1), (2,1), (0,2), (2,2), (0,3), (2,3), (0,4), (1,4), (2,4)],
            '1': [(1,0), (1,1), (1,2), (1,3), (1,4)],
            '2': [(0,0), (1,0), (2,0), (2,1), (0,2), (1,2), (2,2), (0,3), (0,4), (1,4), (2,4)],
            '3': [(0,0), (1,0), (2,0), (2,1), (0,2), (1,2), (2,2), (2,3), (0,4), (1,4), (2,4)],
            '4': [(0,0), (2,0), (0,1), (2,1), (0,2), (1,2), (2,2), (2,3), (2,4)],
            '5': [(0,0), (1,0), (2,0), (0,1), (0,2), (1,2), (2,2), (2,3), (0,4), (1,4), (2,4)],
            '6': [(0,0), (1,0), (2,0), (0,1), (0,2), (1,2), (2,2), (0,3), (2,3), (0,4), (1,4), (2,4)],
            '7': [(0,0), (1,0), (2,0), (2,1), (2,2), (2,3), (2,4)],
            '8': [(0,0), (1,0), (2,0), (0,1), (2,1), (0,2), (1,2), (2,2), (0,3), (2,3), (0,4), (1,4), (2,4)],
            '9': [(0,0), (1,0), (2,0), (0,1), (2,1), (0,2), (1,2), (2,2), (2,3), (0,4), (1,4), (2,4)],
            ':': [(1,1), (1,3)]
        }
        
        # Threads e Estados
        self.listening_thread = None
        self.stop_listening_event = threading.Event()
        self.is_animating = False 
        self.show_clock = False # Estado para alternar entre rosto e relógio
        self.clock_pixels = []
        
        # Iniciar animação
        self.root.after(100, self.start_blink_sequence)

    def setup_default_voice(self):
        voices = self.engine.getProperty('voices')
        # Tenta achar uma voz em português
        for v in voices:
            if "portuguese" in v.name.lower() or "brazil" in v.name.lower():
                self.engine.setProperty('voice', v.id)
                break

    def load_images(self):
        files = sorted([f for f in os.listdir(IMAGE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))])

        self.idle_image = None
        self.blink_sequence = []
        self.spin_sequence = []
        self.heart_sequence = []

        for f in files:
            path = os.path.join(IMAGE_DIR, f)
            try:
                img = Image.open(path).convert("RGBA")
                img = img.resize((512, 256), Image.NEAREST)
                tk_img = ImageTk.PhotoImage(img)

                # Identificar tipo de imagem pelo nome
                if "blink" in f:
                    if f.endswith("_1.png") or "_1." in f:
                        self.idle_image = tk_img
                    else:
                        self.blink_sequence.append(tk_img)
                elif "spin" in f:
                    self.spin_sequence.append(tk_img)
                elif "heart" in f:
                    self.heart_sequence.append(tk_img)

            except Exception as e:
                print(f"Erro ao carregar {f}: {e}")

        if not self.idle_image and self.blink_sequence:
            self.idle_image = self.blink_sequence.pop(0)

    def setup_ui(self):
        # Canvas da Face
        self.canvas_width = 512
        self.canvas_height = 256
        self.face_canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.face_canvas.pack(pady=20, padx=20)
        self.image_on_canvas = self.face_canvas.create_image(0, 0, anchor="nw")
        
        # Painel de Controles
        control_frame = tk.Frame(self.root, bg="#2c3e50")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(control_frame, text="1 Toque (Idol/Hora)", command=self.one_tap_action, width=20).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Segurar (Reação)", command=self.hold_action, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Balançar (Spin)", command=self.shake_action, width=20).grid(row=1, column=0, padx=5, pady=5)
        self.listen_btn = tk.Button(control_frame, text="3 Toques (Ouvir: OFF)", command=self.toggle_listening, width=20, bg="#e74c3c", fg="white")
        self.listen_btn.grid(row=1, column=1, padx=5, pady=5)

    def clear_clock(self):
        for p in self.clock_pixels:
            self.face_canvas.delete(p)
        self.clock_pixels = []

    def run_heart_animation(self):
        self.is_animating = True

        full_seq = []
        # heart_sequence index i is file heart_180526_{i+1}.png
        # So heart 6 and 7 are indices 5 and 6.
        if len(self.heart_sequence) >= 7:
            # Frames 1-5 (indices 0-4) - Velocidade aumentada (100ms)
            for i in range(5):
                full_seq.append((self.heart_sequence[i], 100))
            
            # Repeat frames 6 and 7 five times with 250ms delay (mantém lento)
            for _ in range(5):
                full_seq.append((self.heart_sequence[5], 250))
                full_seq.append((self.heart_sequence[6], 250))
                
            # Rest (indices 7+) - Velocidade aumentada (100ms)
            for i in range(7, len(self.heart_sequence)):
                full_seq.append((self.heart_sequence[i], 100))
        else:
            full_seq = [(img, 100) for img in self.heart_sequence]

        def animate(index):
            if index < len(full_seq):
                img, delay = full_seq[index]
                self.update_face_image(img)
                self.root.after(delay, lambda: animate(index + 1))
            else:
                self.is_animating = False
                self.start_blink_sequence()

        if full_seq:
            animate(0)
        else:
            self.is_animating = False
            self.start_blink_sequence()

    def force_face_mode(self):
        self.show_clock = False
        self.clear_clock()
        self.face_canvas.itemconfig(self.image_on_canvas, state="normal")

    def hold_action(self):
        self.falar("Isso é bom! Estou gostando.")
        self.force_face_mode()
        self.run_heart_animation()

    def update_face_image(self, tk_img):
        if self.show_clock: return
        self.face_canvas.itemconfig(self.image_on_canvas, image=tk_img)

    def start_blink_sequence(self):
        if self.is_animating or self.show_clock: return 
        
        if self.idle_image:
            self.update_face_image(self.idle_image)
            # 7 segundos de idle antes de piscar
            self.root.after(7000, self.run_blink_animation)

    def run_blink_animation(self):
        if self.is_animating or self.show_clock: return
        
        def animate(index):
            if self.is_animating or self.show_clock: return
            if index < len(self.blink_sequence):
                self.update_face_image(self.blink_sequence[index])
                self.root.after(100, lambda: animate(index + 1))
            else:
                self.start_blink_sequence()
        
        if self.blink_sequence:
            animate(0)
        else:
            self.start_blink_sequence()

    def run_spin_animation(self):
        self.is_animating = True
        
        full_seq = []
        if len(self.spin_sequence) >= 12:
            # Frames 1-2 (índices 0-1)
            full_seq.extend(self.spin_sequence[0:2])
            # Frames 3-12 (índices 2-11) repetidos 3 vezes
            for _ in range(3):
                full_seq.extend(self.spin_sequence[2:12])
            # O resto (índice 12 em diante)
            full_seq.extend(self.spin_sequence[12:])
        else:
            full_seq = self.spin_sequence

        def animate(index):
            if index < len(full_seq):
                self.update_face_image(full_seq[index])
                self.root.after(50, lambda: animate(index + 1))
            else:
                self.is_animating = False
                self.start_blink_sequence()
        
        if full_seq:
            animate(0)
        else:
            self.is_animating = False
            self.start_blink_sequence()

    def falar(self, texto):
        print(f"Robô: {texto}")
        def run_tts():
            self.engine.say(texto)
            self.engine.runAndWait()
        threading.Thread(target=run_tts).start()

    def update_clock(self):
        if not self.show_clock:
            self.clear_clock()
            return
            
        agora = datetime.now().strftime("%H:%M")
        self.clear_clock()
        
        # Configurações de escala
        # Cada 'pixel' da matriz 3x5 será um bloco de size x size
        # Original 128x64 -> Escala x4 -> 512x256
        # Se usarmos size=16, cada dígito terá 3*16 = 48px de largura e 5*16 = 80px de altura
        size = 16
        spacing = 16
        total_width = (len(agora) * 3 * size) + ((len(agora) - 1) * spacing)
        x_start = (self.canvas_width - total_width) // 2
        y_start = (self.canvas_height - (5 * size)) // 2
        
        current_x = x_start
        for char in agora:
            if char in self.pixel_digits:
                for px, py in self.pixel_digits[char]:
                    x1 = current_x + (px * size)
                    y1 = y_start + (py * size)
                    x2 = x1 + size
                    y2 = y1 + size
                    rect = self.face_canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")
                    self.clock_pixels.append(rect)
            current_x += (3 * size) + spacing
            
        self.root.after(1000, self.update_clock)

    def one_tap_action(self):
        self.show_clock = not self.show_clock
        
        if self.show_clock:
            # Esconde imagem e mostra relógio
            self.face_canvas.itemconfig(self.image_on_canvas, state="hidden")
            self.update_clock()
        else:
            # Esconde relógio e mostra imagem
            self.clear_clock()
            self.face_canvas.itemconfig(self.image_on_canvas, state="normal")
            self.start_blink_sequence()

        agora = datetime.now()
        self.falar(f"Agora são {agora.hour} e {agora.minute}.")

    def shake_action(self):
        self.falar("Ei! Pare de me balançar, estou ficando tonto!")
        self.force_face_mode()
        self.run_spin_animation()

    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_btn.config(text="3 Toques (Ouvir: ON)", bg="#2ecc71")
            self.stop_listening_event.clear()
            self.listening_thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.listening_thread.start()
        else:
            self.is_listening = False
            self.listen_btn.config(text="3 Toques (Ouvir: OFF)", bg="#e74c3c")
            self.stop_listening_event.set()

    def listen_loop(self):
        r = sr.Recognizer()
        r.pause_threshold = 1.0
        while not self.stop_listening_event.is_set():
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = r.listen(source, timeout=2, phrase_time_limit=5)
                    texto = r.recognize_google(audio, language="pt-BR")
                    print(f"Usuário: {texto}")
                    self.process_command(texto)
                except:
                    continue

    def process_command(self, texto):
        texto = texto.lower()
        if "que horas são" in texto:
            self.one_tap_action()
            return
        
        prompt = f"Responda curto em português: {texto}"
        try:
            response = requests.post(OLLAMA_URL, json={"model": "mistral:latest", "prompt": prompt, "stream": False}, timeout=10)
            self.falar(response.json()["response"].strip())
        except:
            self.falar("Erro na conexão.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()
