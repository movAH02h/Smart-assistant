import pyttsx3
import datetime
import speech_recognition as sr

def get_time_and_date():
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_date = datetime.datetime.now().strftime("%d-%m-%y")
    return f"Сейчас {current_time}, дата {current_date}"

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Скажите что-то:")
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio, language='ru-RU')
        print(f"Вы сказали: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Извините, не удалось распознать речь.")
        return ""
    except sr.RequestError as e:
        print(f"Ошибка при запросе к сервису распознавания речи: {e}")
        return ""

if __name__ == "__main__":
    while True:
        user_input = recognize_speech()

        if "какое сейчас время" in user_input:
            current_time = datetime.datetime.now().strftime("%H:%M")
            print(f"Сейчас {current_time}")
            speak(f"Сейчас {current_time}")
        elif "какое сегодня число" in user_input:
            current_date = datetime.datetime.now().strftime("%d-%m-%y")
            print(f"Сегодня {current_date}")
            speak(f"Сегодня {current_date}")
        elif "пока" in user_input:
            print("До свидания!")
            speak("До свидания")
            break
        else:
            print("Я не поняла Вас, пожалуйста, повторите.")
            speak("Я не поняла Вас, пожалуйста, повторите")


