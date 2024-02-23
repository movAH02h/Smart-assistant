import speech_recognition
from gtts import gTTS
import os
import json
import random
import webbrowser
import urllib.parse
import wikipediaapi
import datetime
import requests
from bs4 import BeautifulSoup
import time
import locale

# import spacy


class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_voice():
    """
    Установка голоса по умолчанию
    """
    # Оставлю эту функцию здесь, но она пока что не нужнаы
    pass


def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента
    """
    tts = gTTS(text=text_to_speech, lang='ru')
    tts.save("assistant_speech.mp3")
    os.system("afplay assistant_speech.mp3")
    os.remove("assistant_speech.mp3")


def audio_record_recognize():
    """
    Запись и распознавание речи
    """
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    with microphone:
        recognized_data = ""
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Слушаю Вас...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Проверьте, включён ли ваш микрофон.")
            return

        try:
            print("Начинаю распознание...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

    return recognized_data


def get_time_of_day():
    """
    Возвращает время суток: утро, день, вечер, ночь
    """
    current_hour = datetime.datetime.now().hour
    if 6 <= current_hour < 12:
        return "утро"
    elif 12 <= current_hour < 18:
        return "день"
    elif 18 <= current_hour < 24:
        return "вечер"
    else:
        return "ночь"


def get_greeting_response(config):
    """
    Получает ответ на приветствие в соответствии с текущим временем суток или рандомный выбор из блока "get_greeting_response"
    """
    time_of_day = get_time_of_day()
    greeting_intent = config["intents"]["get_greeting_response"]
    if time_of_day in ["утро", "день", "вечер", "ночь"]:
        if time_of_day == "утро":
            return greeting_intent["responses"][1]  # Доброе утро
        elif time_of_day == "день":
            return greeting_intent["responses"][0]  # Добрый день
        elif time_of_day == "вечер":
            return greeting_intent["responses"][2]  # Добрый вечер
        else:
            return greeting_intent["responses"][3]  # Доброй ночи
    else:
        return random.choice(greeting_intent["responses"])


# nlp = spacy.load("ru_core_news_sm")


# def extract_city_from_query(query):
#     doc = nlp(query)
#     for token in doc:
#         if token.pos_ == "PROPN":
#             return token.text.capitalize()
#     return None
#
#
# def time_in_city(city_name):
#     """
#     Получает текущее время в указанном городе и произносит его пользователю.
#     """
#     try:
#         # Формируем URL запроса к API для получения текущего времени в указанном городе
#         url = f"http://worldtimeapi.org/api/timezone/{city_name}"
#         response = requests.get(url)
#         # Проверяем успешность запроса
#         if response.status_code == 200:
#             # Извлекаем данные о времени из ответа
#             data = response.json()
#             current_time = data["datetime"]
#             # Произносим время пользователю
#             play_voice_assistant_speech(f"В городе {city_name} сейчас {current_time}")
#         else:
#             play_voice_assistant_speech("Извините, не удалось получить время для указанного города.")
#     except Exception as e:
#         play_voice_assistant_speech("Произошла ошибка при получении времени. Попробуйте еще раз.")

def get_current_date(format_type):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Установка локали для вывода на русском языке
    current_date = datetime.datetime.now()
    day_of_week = current_date.strftime("%A")
    day = current_date.day
    month = current_date.strftime("%B").capitalize()  # Форматируем месяц с большой буквы
    year = current_date.year

    if format_type == "full_date":
        return f"Сегодня {day_of_week}, {day} {month} {year} года."
    elif format_type == "day_of_week":
        return f"Сегодня {day_of_week}."
    elif format_type == "day":
        return f"Сегодня {day} {month}, {day_of_week}."
    elif format_type == "month":
        return f"Сейчас идёт {month}."
    elif format_type == "year":
        return f"Сейчас {year}."


def handle_intent(intent, config):
    """
    Обработка намерений пользователя
    """
    if intent in config["intents"]:
        responses = config["intents"][intent]["responses"]
        examples = config["intents"][intent]["examples"]
        current_date = None
        if intent == "farewell":
            play_voice_assistant_speech(random.choice(responses))
            exit()  # Завершаем программу после прощания
        elif intent == "greeting":
            play_voice_assistant_speech(random.choice(responses))
        elif intent == "get_greeting_response":
            play_voice_assistant_speech(get_greeting_response(config))
        elif intent == "google_search":
            play_voice_assistant_speech(random.choice(responses))
            user_query = audio_record_recognize()
            encoded_query = urllib.parse.quote(user_query)
            webbrowser.open_new_tab(f"https://www.google.com/search?q={encoded_query}")
            # Ждем несколько секунд для загрузки страницы
            time.sleep(5)
            # Получаем HTML-код страницы результатов поиска
            search_results_page = requests.get(f"https://www.google.com/search?q={encoded_query}")
            soup = BeautifulSoup(search_results_page.content, 'html.parser')
            # Ищем все заголовки и ссылки на странице результатов
            titles = soup.find_all('h3')
            links = soup.find_all('a')
            # Выводим название сайта и URL первых трех ссылок
            for title, link in zip(titles[:3], links[:3]):
                link_text = title.text
                # link_url = link.get('href')
                # Получаем доменное имя из URL
                # domain = re.findall(r'https?://(?:www\.)?(.*?)/', link_url)[0]
                print(f"{link_text}")
            play_voice_assistant_speech("Вот, что мне удалось найти по вашему запросу.")
        elif intent == "youtube_search":
            play_voice_assistant_speech(random.choice(responses))
            user_query = audio_record_recognize()
            encoded_query = urllib.parse.quote(user_query)
            webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={encoded_query}")
        elif intent == "wikipedia_search":
            play_voice_assistant_speech(random.choice(responses))
            user_query = audio_record_recognize()
            wiki_wiki = wikipediaapi.Wikipedia(
                language='ru',
                user_agent='SmartAssistant/1.0'
            )
            page = wiki_wiki.page(user_query)
            if page.exists():
                play_voice_assistant_speech(page.summary)
            else:
                play_voice_assistant_speech("По вашему запросу ничего не найдено в Википедии.")

        elif intent == "checking_time":
            current_time = datetime.datetime.now().strftime("%H:%M")
            play_voice_assistant_speech(f"Сейчас {current_time}")
        elif intent == "current_date":
            if "какая сегодня дата" in examples:
                current_date = get_current_date("full_date")
            elif "какой сегодня день недели" in examples:
                current_date = get_current_date("day_of_week")
            elif "какой сегодня день" in examples:
                current_date = get_current_date("day")
            elif "какой месяц сейчас" in examples:
                current_date = get_current_date("month")
            elif "какой сейчас год" in examples:
                current_date = get_current_date("year")
            play_voice_assistant_speech(current_date)
        # elif intent == "time_in_city":
        #     examples = config["intents"][intent]["examples"]
        #     play_voice_assistant_speech(random.choice(examples))
        #     user_query = audio_record_recognize()
        #     city = extract_city_from_query(user_query)
        #     if city:
        #         time_in_city(city)
        #     else:
        #         play_voice_assistant_speech("К сожалению, я не могу определить город. Пожалуйста, укажите его явно.")
    else:
        play_voice_assistant_speech(config["failure_phrases"])


def main():
    with open("config.json", "r") as file:
        config = json.load(file)

    try:
        while True:
            voice_input = audio_record_recognize()
            print("Вы сказали:", voice_input)

            for intent, data in config["intents"].items():
                for example in data["examples"]:
                    if example in voice_input:
                        handle_intent(intent, config)
                        break
    finally:
        # Удаляем файл microphone-results.wav по завершении работы программы
        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")


if __name__ == "__main__":
    main()
