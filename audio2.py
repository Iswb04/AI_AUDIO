import requests
import pyttsx3
import time
import speech_recognition as sr

def falar(texto):
    print("IA:", texto)
    engine = pyttsx3.init()
    engine.setProperty('rate', 220)
    engine.say(texto)
    engine.runAndWait()

def ouvir():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Fale algo...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        texto = r.recognize_google(audio, language="pt-BR")
        print("Você:", texto)
        return texto
    except:
        print("Não entendi...")
        return None

while True:
    user = ouvir()

    if not user:
        continue

    if user.lower() in ["sair", "exit", "quit"]:
        break

    prompt = f"""
    Regras:
    - Fale sempre em português
    - Fale no máximo um parágrafo

    Usuário: {user}
    Resposta:
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    resposta = response.json()["response"].strip()

    time.sleep(0.3)

    falar(resposta)