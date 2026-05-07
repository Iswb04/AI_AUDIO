import requests
import pyttsx3
import time
import speech_recognition as sr
import os
import pyautogui

def falar(texto):
    print("IA:", texto)
    engine = pyttsx3.init()
    engine.setProperty('rate', 220)
    engine.say(texto)
    engine.runAndWait()

def ouvir():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False # corta ruido
    r.pause_threshold = 3.0 # tempo de silencio
    r.phrase_time_limit = 30 # tempo de fala total

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Ouvindo...")
        try:
            audio = r.listen(source, timeout=None, phrase_time_limit=10)
        except Exception:
            return None

    try:
        print("Processando áudio...")
        texto = r.recognize_google(audio, language="pt-BR")
        print("Você disse:", texto)
        return texto
    except:
        return None

def executar_comando_local(texto):
    texto = texto.lower()
    if "abrir chrome" in texto:
        os.system("start chrome.exe")
        return "Abrindo Chrome"
    if "abrir steam" in texto:
        os.startfile(r"C:\Program Files (x86)\Steam\steam.exe")
        return "Abrindo Steam"
    if "fechar chrome" in texto:
        pyautogui.hotkey("ctrl", "w")
        return "Chrome fechado"
    if "fechar steam" in texto:
        os.system("taskkill /IM steam.exe /F")
        return "Fechando Steam"
    return None

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
            prompt = f"Fale sempre em português. Responda com no máximo uma frase.\nUsuário: {comando_limpo}\nResposta:"
            
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:latest",
                        "prompt": prompt,
                        "stream": False,
                    }
                )
                resposta_ai = response.json()["response"].strip()
                falar(resposta_ai)
            except Exception as e:
                falar("Erro ao conectar com o Ollama.")
    else:
        print(f"Ignorando: '{frase_min}'")