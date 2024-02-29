import speech_recognition
import pyttsx3
from fuzzywuzzy import fuzz
import datetime
import pyowm
from pyowm.utils.config import get_default_config
import wikipediaapi
import time
import urllib.parse
from bs4 import BeautifulSoup
import requests
import json
import random
import locale
import webbrowser


with open("commands.json", "r", encoding='utf-8') as file:
    options = json.load(file)

def get_time_and_date():
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_date = datetime.datetime.now().strftime("%d-%m-%y")
    return f"Сейчас {current_time}, дата {current_date}"

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


def get_greeting_response():
    """
    Получает ответ на приветствие в соответствии с текущим временем суток или рандомный выбор из блока "get_greeting_response"
    """
    time_of_day = get_time_of_day()
    greeting_intent = options["cmds"]["get_greeting_response"]
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

def get_current_date(format_type):
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')  # Установка локали для вывода на русском языке
    current_date = datetime.datetime.now()
    day_of_week = current_date.strftime("%A")
    print(day_of_week)
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

def say(frase):
    engine = pyttsx3.init()
    engine.setProperty('volume', 'ru')
    try:
        engine.say(frase)
        engine.runAndWait()
    except RuntimeError:
        print("Функция уже запущена...")


def recognise_better(command):
    real_command = ''
    edit_distance_percent = 0

    for key, value in options["cmds"].items(): # Возвращает кортеж пар (ключ - значение)
        for exist_command in value["examples"]:
            percent = fuzz.ratio(command, exist_command)
            if (percent > edit_distance_percent):
                edit_distance_percent = percent
                real_command = key
    if (edit_distance_percent >= 50):
        return real_command
    return ""

def do_command(command):
    if command in options["cmds"]:
        responses = options["cmds"][command]["responses"]
        examples = options["cmds"][command]["examples"]
        if (command == "greeting"):
            say("Привет, друг!")
        elif (command == "ctime"):
            current_time = datetime.datetime.now().strftime("%H:%M")
            print(f"Сейчас {current_time}")
            say(f"Сейчас {current_time}")
        elif (command == "cdate"):
            current_date = ""
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
            say(current_date)
        elif (command == "get_greeting_response"):
            say(get_greeting_response())
        elif (command == "weather_forecast"):

            config_dict = get_default_config()
            config_dict['language'] = 'ru'
            owm = pyowm.OWM('1caaa63b8672e96b288306695fd081ed', config_dict)
            manager = owm.weather_manager()

            say(random.choice(responses))
            city = listen() # прослушка города

            weather = manager.weather_at_place(city).weather
            forecast = weather.detailed_status

            temperature = weather.temperature('celsius').get('temp')
            temperature = round(temperature)

            # говорит города юез склонений
            say(f'Температура в {city} сейчас {temperature}, {forecast}')
        elif command == "google_search":

            say(random.choice(responses))
            user_query = listen()
            encoded_query = urllib.parse.quote(user_query)
            webbrowser.open_new_tab(f"https://www.google.com/search?q={encoded_query}")
            # Ждем несколько секунд для загрузки страницы
            time.sleep(3)
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
            say("Вот, что мне удалось найти по вашему запросу.")
        elif command == "youtube_search":
            say(random.choice(responses))

            user_query = listen()

            encoded_query = urllib.parse.quote(user_query)
            webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={encoded_query}")
        elif command == "wikipedia_search":
            say(random.choice(responses))

            user_query = listen()

            wiki_wiki = wikipediaapi.Wikipedia(
                language='ru',
                user_agent='SmartAssistant/1.0'
            )
            page = wiki_wiki.page(user_query)
            if page.exists():
                text = page.summary # некоторые ответы получаются ужасно. Надо как-то это исправлять хз
                with open("wiki_result.txt", "w", encoding='utf-8') as file:
                    file.write(text)

                say(text)
            else:
                say("По вашему запросу ничего не найдено в Википедии.")
        elif (command == "joke"):
            say(random.choice(responses))
        elif (command == "fairytale"):
            say(random.choice(responses))
    else:
        say("Не совсем поняла, давайте еще раз!")

def listen():
    recog = speech_recognition.Recognizer()
    recog.pause_threshold = 0.5
    with speech_recognition.Microphone() as mic:
        recog.adjust_for_ambient_noise(source=mic, duration=0.5)

        print("Я вас слушаю >>> ")
        audio = recog.listen(mic)

        try:
            text = recog.recognize_google(audio_data=audio, language='ru').lower()

        except speech_recognition.RequestError:
            return "Неизвестная ошибка, проверьте подключение к интернету"
        except speech_recognition.UnknownValueError:
            return "Ошибка распознавания"

    return text

def click():
    text = listen()# слушает

    result = recognise_better(text)# подбирает команду, которая больше всего подходит (fuzzywuzzy)

    do_command(result)# выполнение команды




