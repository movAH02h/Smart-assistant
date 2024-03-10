import os.path
from fuzzywuzzy import fuzz
import pyowm
import sys
from pyowm.utils.config import get_default_config
import random
import queue
import sounddevice as sd
import vosk
import pyttsx3
import data_set
import json
import datetime
import time
import wikipediaapi
import urllib.parse
from bs4 import BeautifulSoup
from googletrans import Translator
import webbrowser
import requests

class NotFoundException(Exception):
    pass

q = queue.Queue()
model = vosk.Model('../model_small')
device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])

def search_google(text = ""):
    user_query = text
    if not user_query:
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
    if not text:
        say("Вот, что мне удалось найти по вашему запросу.")

def ctime():
    current_time = datetime.datetime.now().strftime("%H:%M")
    print(f"Сейчас {current_time}")
    say(f"Сейчас {current_time}")

def translate_to_english():
    text = listen()

    translator = Translator()
    try:
        translation = translator.translate(text, dest='en', src='ru')
        print(translation.text)
        say(f"перевод звучит так: {translation.text}")
    except AttributeError as e:
        say("ошибка распознавания. попробуйте еще раз")

def search_recipe():
    #инкапсуляция + в обычном переводе надо спрашивать слово, а здесь это вспомогательная ф-я
    def russian_to_english(text):
        translator = Translator()
        try:
            translation = translator.translate(text, dest='en', src='ru')
            return translation.text
        except AttributeError as e:
            return -1

    def english_to_russian(text):
        translator = Translator()
        try:
            translation = translator.translate(text, dest='ru', src='en')
            return translation.text
        except AttributeError as e:
            return -1
    """
    Поиск рецепта по запросу пользователя с помощью API The Meal DB
    """
    query = listen()

    translated_query = russian_to_english(query)
    if (translated_query == -1):
        say("небольшая ошибочка попробуйте еще раз пожалуйста")
        return

    print(translated_query)

    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={translated_query}"
    response = requests.get(url)
    data = response.json()

    if data['meals']:
        meal = data['meals'][0]
        recipe_name = english_to_russian(meal['strMeal'])
        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            if ingredient:
                ingredients.append(english_to_russian(ingredient))
            else:
                break

        instructions = english_to_russian(meal['strInstructions'])

        recipe_text = f"Рецепт блюда {recipe_name}:"
        recipe_text += "\n\nИнгредиенты:"
        for ingredient in ingredients:
            recipe_text += f"\n- {ingredient}"
        recipe_text += f"\n\nИнструкции по приготовлению:\n{instructions}"

        print(recipe_text)
    else:
        say("к сожалению в моей базе данных нет такого рецепта. Вот результаты поиска в гугл. Может вам пригодится")
        search_google(query)

def search_youtube():
    user_query = listen()

    encoded_query = urllib.parse.quote(user_query)
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={encoded_query}")

def to_do_list_create():
    if (os.path.exists("to_do_list.txt")):
        say("такой список уже есть")
    else:
        file = open("to_do_list.txt", "w")
        file.close()
        say("создан список задач")

def to_do_list_add():
    if (os.path.exists("to_do_list.txt")):
        data = listen()
        file = open("to_do_list.txt", "a+", encoding='utf8')
        file.write(data + "\n")
        file.close()
        say(f"Задача '{data}' добавлена в список дел.")
    else:
        say("Список задач для начала нужно создать. Для этого скажите кеша создай список задач")

def to_do_list_show():
    try:
        file = open("to_do_list.txt", "r", encoding='utf-8')
        content = file.readlines()
        for line in content:
            say(line)
        file.close()
    except FileExistsError:
        print("no")
        say("Список задач не создан")

def to_do_list_remove():
    task = listen()
    file = open("to_do_list.txt", "r+", encoding='utf-8')
    content = list(file.readlines())
    print(content)
    total_rate, line = 0, ""
    for element in content:
        current_rate = fuzz.ratio(element, task)
        if (current_rate > total_rate):
            total_rate = current_rate
            line = element

    print(line)

    content.remove(line)
    file.seek(0)

    for element in content:
        file.write(element)

    #усечение файла до текущей позиции курсора (чтобы полностью перезаписать файл)
    file.truncate()

    file.close()

def search_wikipedia():

    user_query = listen()

    wiki_wiki = wikipediaapi.Wikipedia(
        language='ru',
        user_agent='SmartAssistant/1.0')
    page = wiki_wiki.page(user_query)
    if page.exists():
        text = page.summary  # некоторые ответы получаются ужасно. Надо как-то это исправлять хз
        with open("wiki_result.txt", "w", encoding='utf-8') as file:
            file.write(text)

        say(text)
    else:
        say("По вашему запросу ничего не найдено в Википедии.")

def offwork():
    sys.exit()

def weather():

    config_dict = get_default_config()
    config_dict['language'] = 'ru'
    owm = pyowm.OWM('1caaa63b8672e96b288306695fd081ed', config_dict)
    manager = owm.weather_manager()

    city = listen()

    try:
        weather = manager.weather_at_place(city).weather
        forecast = weather.detailed_status

        temperature = weather.temperature('celsius').get('temp')
        temperature = round(temperature)

        # говорит города юез склонений
        say(f'Температура в {city} сейчас {temperature}, {forecast}')
    except Exception:
        say("Похоже город неверный!")

def joke():
    try:
        file = open("jokes.txt", "r", encoding='utf8')
        funs = list(file.readlines())
        file.close()
        say(random.choice(funs))
    except FileExistsError:
        print("ОШИБКА: Файл с шутками не найден")

def passive():
    pass

def say(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)

    engine.say(text)
    engine.runAndWait()

def recognise(data, vectorizer, clf):
    trg = data_set.triggers.intersection(data.split())
    if not trg:
        return
    data.replace(list(trg)[0], '')
    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]

    func_name = answer.split()[0]
    say(answer.replace(func_name, ''))
    print(func_name)
    exec(func_name + '()')

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    print("Я вас слушаю >>>")
    with sd.RawInputStream(samplerate=samplerate, blocksize=16000, device=device[0],
                    dtype='int16', channels=1, callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            #когда будет пауза он выводит весь получившийся текст
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                print(data)
                return data
def click(vectorizer, clf):
    while True:
        data = listen()
        recognise(data, vectorizer, clf)

