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
    engine.stop()
    engine.say(texto)
    engine.runAndWait()


def ouvir():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 2.5

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Aguardando fala...")

        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            falar("Nenhum som detectado. Encerrando programa.")
            return "EXIT"

    try:
        print("Processando áudio...")
        texto = r.recognize_google(audio, language="pt-BR")
        print("Você:", texto)
        return texto

    except sr.UnknownValueError:
        falar("Não consegui entender o áudio.")
        return None

    except sr.RequestError:
        falar("Erro no serviço de reconhecimento.")
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


while True:
    user = ouvir()

    if user == "EXIT":
        break

    if not user:
        continue

    if user.lower() in ["sair", "exit", "quit", "finalizar", "encerrar"]:
        break

    comando = executar_comando_local(user)

    if comando:
        falar(comando)
        continue

    prompt = f"""
    Regras:
    - Fale sempre em português.
    - Responda com uma frase SEMPRE.

    Usuário: {user}
    Resposta:
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }
    )

    resposta = response.json()["response"].strip()

    time.sleep(0.3)
    falar(resposta)