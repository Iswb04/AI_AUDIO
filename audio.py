import requests
import pyttsx3
import time

def falar(texto):
    print("IA:", texto)
    engine = pyttsx3.init()
    engine.setProperty('rate', 220)
    engine.say(texto)
    engine.runAndWait()

while True:
    user = input("Você: ")

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

    print("[Enviando via Bluetooth...]")
    time.sleep(0.5)

    falar(resposta)