import requests
import pyttsx3
import time
import speech_recognition as sr



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
    r.pause_threshold = 0.8

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


while True:
    user = ouvir()

    if user == "EXIT":
        break

    if not user:
        continue

    if user.lower() in ["sair", "exit", "quit", "finalizar", "encerrar"]:
        break

    prompt = f"""
    Regras:
    - Fale sempre em português.
    - Fale o minimo possivel para responder.

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