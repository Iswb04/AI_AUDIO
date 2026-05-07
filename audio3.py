import requests
import pyttsx3
import speech_recognition as sr
import os
import pyautogui
import tkinter as tk
import threading
from datetime import datetime

agora = datetime.now()

# config visual - tkinter
def iniciar_tk():
    global janela
    janela = tk.Tk()
    janela.overrideredirect(True)
    janela.geometry("50x50+0+0")
    janela.attributes("-topmost", True)
    janela.mainloop()
    

def mudar_cor(cor):
    global janela
    try:
        janela.configure(bg=cor)
        janela.update()
    except:
        pass

threading.Thread(target=iniciar_tk, daemon=True).start()

# funçoes de voz
def falar(texto):
    print("IA:", texto)
    engine = pyttsx3.init()
    engine.setProperty('rate', 220)
    engine.say(texto)
    engine.runAndWait()

def ouvir():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.pause_threshold = 2.0

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)

        #Verde quando estiver ouvindo
        mudar_cor("green") 
        print("Ouvindo...")

        try:
            audio = r.listen(source, timeout=None, phrase_time_limit=10)
        except Exception:
            mudar_cor("green")
            return None

    try:
        # Amarelo quando estiver processando o áudio
        mudar_cor("yellow")
        print("Processando áudio...")

        texto = r.recognize_google(audio, language="pt-BR")
        print("Você disse:", texto)
        
        return texto
    except:
        mudar_cor("green")
        return None

# comandos locais
def executar_comando_local(texto):
    texto = texto.lower()

    if "que horas são" in texto:
        return f"são {agora.hour} e {agora.minute}"

    if "abrir chrome" in texto:
        os.system("start chrome.exe")
        return "Abrindo Chrome"

    if "abrir steam" in texto:
        caminhos_steam = [
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe"
        ]
        for caminho in caminhos_steam:
            if os.path.exists(caminho):
                os.startfile(caminho)
                return "Abrindo Steam"
        return "Steam não encontrada"

    if "fechar chrome" in texto:
        pyautogui.hotkey("ctrl", "w")
        return "Chrome fechado"

    if "fechar steam" in texto:
        os.system("taskkill /IM steam.exe /F")
        return "Fechando Steam"

    return None

# loop principal
WAKE_WORD = "python"

while True:
    user_input = ouvir()

    if not user_input:
        continue

    frase_min = user_input.lower()

    if frase_min.startswith(WAKE_WORD):
        comando_limpo = frase_min.replace(WAKE_WORD, "").strip()

        if not comando_limpo:
            falar("Sim? Estou ouvindo.")
            continue

        if comando_limpo in ["sair", "exit", "quit", "finalizar", "encerrar"]:
            falar("Desligando.")
            break

        comando_executado = executar_comando_local(comando_limpo)

        if comando_executado:
            falar(comando_executado)
        else:
            # PROCESSAMENTO COM OLLAMA
            prompt = f"""
            Regras:
            - Fale sempre em português.
            - Responda com uma frase SEMPRE.

            Usuário: {comando_limpo}
            Resposta:
            """

            try:
                # Mantém amarelo enquanto a IA pensa
                mudar_cor("yellow")

                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "mistral:latest",
                        "prompt": prompt,
                        "stream": False,
                    }
                )

                resposta_ai = response.json()["response"].strip()
                
                # Volta para verde antes de falar/esperar novo comando
                mudar_cor("green")
                falar(resposta_ai)

            except Exception:
                mudar_cor("green")
                falar("Erro ao conectar com o Ollama.")
    else:
        # Se não ouviu a Wake Word, volta para verde
        mudar_cor("green")
        print(f"Ignorando: '{frase_min}'")