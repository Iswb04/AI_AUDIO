import requests
import pyttsx3
import time
import speech_recognition as sr
import os
import pyautogui

wake_word = "olá teste"
estado = "sleep"

print("programa iniciado.")

r = sr.Recognizer()
r.dynamic_energy_threshold = True
r.pause_threshold = 2.5
mic = sr.Microphone()

# calibração
with mic as source:
    r.adjust_for_ambient_noise(source, duration=1)


def falar(texto):
    print("IA:", texto)
    engine = pyttsx3.init()
    engine.setProperty('rate', 220)
    engine.say(texto)
    engine.runAndWait()


def ouvir():
    with mic as source:
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            return None

    try:
        return r.recognize_google(audio, language="pt-BR")
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


def modo_assistente():
    global estado

    falar("Sim?")

    while estado == "active":
        comando = ouvir()
        if not comando:
            continue

        comando = comando.lower()

        # trascrição de audio
        print("Você:", comando)

        # voltar pro sleep
        if comando in ["parar", "voltar", "desligar"]:
            estado = "sleep"
            falar("Ok")
            break

        resultado = executar_comando_local(comando)
        if resultado:
            falar(resultado)
            continue

        prompt = f"""
Responda em português com apenas uma frase.

Usuário: {comando}
Resposta:
"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                }
            )

            resposta = response.json()["response"].strip()

            falar(resposta)

        except:
            falar("Erro na IA.")


# WAKE WORD
while True:

    if estado == "sleep":
        texto = ouvir()

        if texto and wake_word in texto.lower():
            estado = "active"
            modo_assistente()

    time.sleep(0.2)