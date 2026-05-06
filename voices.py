import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for i, v in enumerate(voices):
    print(i, v.name)

for i, v in enumerate(voices):
    print(f"Testando voz {i}")
    engine.setProperty('voice', v.id)
    engine.say("Testando esta voz")
    engine.runAndWait()