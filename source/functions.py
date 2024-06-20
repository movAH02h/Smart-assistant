# Сделать так чтобы голосовой помощник отвечал без имени на обычные фразы, а на active только с именем
import os.path
from fuzzywuzzy import fuzz
import pyowm
import numpy as np
import sys
from pycbrf import ExchangeRates
from pyowm.utils.config import get_default_config
import random
import queue
from num2words import num2words
import sounddevice as sd
import vosk
import locale
import json
import datetime
import time
import wikipediaapi
import urllib.parse
from bs4 import BeautifulSoup
from googletrans import Translator
import webbrowser
import requests
from tensorflow import keras
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pymorphy2
import voice_assistant_data.back_information as bi

class NotFoundException(Exception):
    pass

q = queue.Queue()
model = vosk.Model('../model_small')
device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])

def search_google(speak_model_ru, speak_model_en = None, text=""):
    if text == "":
        user_query = listen()
    else:
        user_query = text

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

    say("Вот, что мне удалось найти по вашему запросу.", speak_model_ru)

def help(speak_model_ru, speak_model_en=None):
    try:
        with open("../voice_assistant_data/abilities.txt", "r", encoding='utf-8') as file:
            information = file.readlines()

        for lines in information:
            print(lines, end=' ')
    except:
        print("file is not found.")
        say("что-то пошло не так.", speak_model_ru)


def coin(speak_model_ru, speak_model_en=None):

    result = random.randint(1, 2)

    if result == 1:
        say('Вам выпала решка.', speak_model_ru)
    else:
        say('Вам выпал орёл.', speak_model_ru)


def translate_to_text(speak_model_ru, speak_model_en=None):
    try:
        file = open("../user_results/speech_to_text.txt", 'w', encoding='utf-8')
        text = listen()
        file.write(text)
        file.close()
    except:
        print("ошибка открытия файла")
        say("что-то пошло не так.", speak_model_ru)


def checking_time(speak_model_ru, speak_model_en=None):
    def declension(n, form_0, form_1, form_2):
        units = n % 10
        tens = (n // 10) % 10
        if tens == 1:
            return form_0
        if units in [0, 5, 6, 7, 8, 9]:
            return form_0
        if units == 1:
            return form_1
        if units in [2, 3, 4]:
            return form_2

    current_time = datetime.datetime.now().strftime("%H:%M").split(':')

    hours = num2words(current_time[0], lang='ru', to='cardinal')
    hours_word = declension(int(current_time[0]), 'часов', 'час', 'часа')

    minutes = num2words(current_time[1], lang='ru', to='cardinal')
    minutes_word = declension(int(current_time[1]), 'минут', 'минута', 'минуты')

    say(f'Сейчас {hours} {hours_word} и {minutes} {minutes_word}.', speak_model_ru)


def cash_rate(speak_model_ru, speak_model_en=None):
    def declension(number, form_0, form_1, form_2):
        units = number % 10
        tens = (number // 10) % 10

        if tens == 1:
            return form_0
        elif units == 1:
            return form_1
        elif units in [2, 3, 4]:
            return form_2
        elif units in [5, 6, 7, 8, 9]:
            return form_0

    currency = listen()
    total_rate = 0
    value = ''
    for name in bi.money:
        current_rate = fuzz.ratio(name, currency)
        if current_rate > total_rate:
            total_rate = current_rate
            value = name

    if total_rate > 30:
        currency = value
    else:
        currency = ''

    if currency in bi.money.keys():
        value = bi.money[currency]
        rates = ExchangeRates(str(datetime.datetime.now())[:10])
        currency_data = list(filter(lambda el: el.code == value, rates.rates))[0]

        value = str(round(currency_data.rate, 2)).split('.')
        print(value)
        rubles_word = declension(int(value[0]), 'рублей', 'рубль', 'рубля')
        pennies_word = declension(int(value[1]), 'копеек', 'копейка', 'копейки')

        rubles_number = num2words(int(value[0]), lang='ru')
        pennies_number = num2words(int(value[1]), lang='ru').split()


        morph = pymorphy2.MorphAnalyzer(lang='ru')
        try:
            pennies_number[-1] = morph.parse(pennies_number[-1])[0].inflect({'nomn', 'femn'}).word
            pennies_number = ' '.join(pennies_number)
        except Exception:
            pennies_number = ' '.join(pennies_number)
            pass

        answer = currency + ' ' + rubles_number + ' ' + rubles_word + ' ' + pennies_number + ' ' + pennies_word + '.'
        say(answer, speak_model_ru)
    else:
        say("я пока не знаю о такой валюте.", speak_model_ru)


def current_date(speak_model_ru, speak_model_en=None):
    def get_appropriate_form_of_date(day, month, year):
        morph = pymorphy2.MorphAnalyzer(lang='ru')

        day = num2words(day, lang='ru', to='ordinal').split()
        day[-1] = morph.parse(day[-1])[0].inflect({'neut', 'nomn'}).word
        day = ' '.join(day)

        month = morph.parse(month)[0].inflect({'gent'}).word

        year = num2words(year, lang='ru', to='ordinal').split()
        year[-1] = morph.parse(year[-1])[0].inflect({'neut', 'gent'}).word
        year = ' '.join(year)

        return day, month, year

    locale.setlocale(locale.LC_TIME, 'ru')  # Установка локали для вывода на русском язык
    date = datetime.datetime.now()

    day = date.day
    day_of_week = date.strftime("%A")
    month = date.strftime("%B")  # Форматируем месяц с большой буквы
    year = date.year

    day, month, year = get_appropriate_form_of_date(day, month, year)

    say(f"Сейчас {day_of_week}, {day} {month} {year} года.", speak_model_ru)


def translate_to_english(speak_model_ru, speak_model_en=None):
    text = listen()

    translator = Translator()
    try:
        translation = translator.translate(text, dest='en', src='ru')
        print(translation.text)
        say_english(f'{translation.text}.', speak_model_en)
    except AttributeError:
        say("ошибка распознавания. Попробуйте еще раз.", speak_model_ru)

def search_recipe(speak_model_ru, speak_model_en=None):
    def russian_to_english(text):
        translator = Translator()
        try:
            translation = translator.translate(text, dest='en', src='ru')
            return translation.text
        except AttributeError:
            return -1

    def english_to_russian(text):
        translator = Translator()
        try:
            translation = translator.translate(text, dest='ru', src='en')
            return translation.text
        except AttributeError:
            return -1
    """
    Поиск рецепта по запросу пользователя с помощью API The Meal DB
    """
    query = listen()

    translated_query = russian_to_english(query)
    if (translated_query == -1):
        say("небольшая ошибочка попробуйте еще раз пожалуйста.", speak_model_ru)
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

        try:
            file = open("../user_results/recipe.txt", 'w', encoding='utf-8')
            file.write(recipe_text)
            file.close()
            say("записал вам информация в файл.", speak_model_ru)
        except:
            print("не удалось записать в файл")

    else:
        say("к сожалению в моей базе данных нет такого рецепта. Вот результаты поиска в гугл. Может вам пригодится.", speak_model_ru)
        search_google(speak_model_ru, speak_model_en, query)

def search_youtube(speak_model_ru, speak_model_en=None):
    user_query = listen()

    encoded_query = urllib.parse.quote(user_query)
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={encoded_query}")
    say("Приятного просмотра.", speak_model_ru)

def to_do_list_create(speak_model_ru, speak_model_en=None):
    if (os.path.exists("../user_results/to_do_list.txt")):
        say("такой список уже есть.", speak_model_ru)
    else:
        try:
            file = open("../user_results/to_do_list.txt", "w", encoding='utf-8')
            file.close()
            say("создан список задач.", speak_model_ru)
        except:
            print("не удалось создать список задач")


def to_do_list_add(speak_model_ru, speak_model_en=None):
    try:
        data = listen()
        file = open("../user_results/to_do_list.txt", "a+", encoding='utf8')
        file.write(data + ".\n")
        file.write("--------------------------------------")
        file.close()
        say(f"Задача '{data}' добавлена в список дел.", speak_model_ru)
    except FileExistsError:
        say("Список задач для начала нужно создать. Для этого скажите кеша создай список задач.", speak_model_ru)


def to_do_list_show(speak_model_ru, speak_model_en=None):
    try:
        file = open("../user_results/to_do_list.txt", "r", encoding='utf-8')
        content = file.readlines()
        for line in content:
            say(line, speak_model_ru)
        file.close()
    except FileExistsError:
        print("no")
        say("Список задач не создан.", speak_model_ru)


def to_do_list_remove(speak_model_ru, speak_model_en=None):
    try:
        task = listen()
        file = open("../user_results/to_do_list.txt", "r+", encoding='utf-8')
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

        # усечение файла до текущей позиции курсора (чтобы полностью перезаписать файл)
        file.truncate()

        file.close()
    except FileExistsError:
        say("сначала надо создать файл с задачами.", speak_model_ru)


def send_message_to_all(speak_model_ru, speak_model_en=None):

    mail = 'KARum2004@yandex.ru'
    message = listen()

    password = ''
    try:
        file = open("../voice_assistant_data/password_for_smtp.txt", 'r', encoding='utf-8')
        password = file.readline()
        file.close()
    except:
        say("что-то не так с паролем от почты", speak_model_ru)

    msg = MIMEText(f'{message}', 'plain', 'utf-8')
    msg['Subject'] = Header('От голосового помощника Кеши', 'utf-8')
    msg['From'] = mail

    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465, timeout=10)

    try:
        server.login(mail, password)
        for other_mail in bi.posts.values():
            msg['To'] = other_mail
            server.sendmail(msg['From'], other_mail, msg.as_string())
        server.quit()
        say("выполнено", speak_model_ru)

    except Exception as _ex:
        say("не получилось войти в почту при отправке.", speak_model_ru)


def send_message_to_one(speak_model_ru, speak_model_en=None):

    name = listen()
    current_rate = 0
    other_mail = ''

    for key in bi.posts.keys():
        rate = fuzz.ratio(key, name)
        if rate > current_rate:
            current_rate = rate
            other_mail = bi.posts[key]

    if (current_rate < 70):
        say("такого человека я не знаю. Попробуйте заново", speak_model_ru)
        return

    mail = 'KARum2004@yandex.ru'
    say("что написать в письме.", speak_model_ru)
    message = listen()

    password = ''
    try:
        file = open("../voice_assistant_data/password_for_smtp.txt", 'r', encoding='utf-8')
        password = file.readline()
        file.close()
    except:
        say("что-то не так с паролем от почты.", speak_model_ru)

    msg = MIMEText(f'{message}', 'plain', 'utf-8')
    msg['Subject'] = Header('От голосового помощника Кеши', 'utf-8')
    msg['From'] = mail
    msg['To'] = other_mail
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465, timeout=10)

    try:
        server.login(mail, password)
        server.sendmail(msg['From'], other_mail, msg.as_string())
        server.quit()
        say("письмо отправлено.", speak_model_ru)
    except Exception as _ex:
        # Неправильно значит ввели пользователя, его надо удалить
        say("не получилось войти в почту при отправке.", speak_model_ru)



def search_wikipedia(speak_model_ru, speak_model_en=None):

    user_query = listen()

    wiki_wiki = wikipediaapi.Wikipedia(
        language='ru',
        user_agent='SmartAssistant/1.0')
    page = wiki_wiki.page(user_query)
    if page.exists():
        text = page.summary
        try:
            file = open('../user_results/wiki_result.txt', 'w', encoding='utf-8')
            file.write(text)
            file.close()
            say("записал в файл результат поиска.", speak_model_ru)
        except:
            say("что-то пошло не так при открытии файла.", speak_model_ru)
            print("не удалось записать в файл")
    else:
        say("По вашему запросу ничего не найдено в Википедии.", speak_model_ru)

def offwork(speak_model_ru, speak_model_en=None):
    sys.exit()


def weather_forecast(speak_model_ru, speak_model_en=None):
    def declension(number, form_0, form_1, form_2):
        units = number % 10
        tens = (number // 10) % 10

        if tens == 1:
            return form_0
        elif units == 1:
            return form_1
        elif units in [2, 3, 4]:
            return form_2
        elif units in [5, 6, 7, 8, 9]:
            return form_0

    config_dict = get_default_config()
    config_dict['language'] = 'ru'
    owm = pyowm.OWM('1caaa63b8672e96b288306695fd081ed', config_dict)
    manager = owm.weather_manager()

    city = listen()
    try:
        weather = manager.weather_at_place(city).weather
        forecast = weather.detailed_status

        temperature = weather.temperature('celsius').get('temp')
        degree_word = declension(temperature, 'градусов', 'градус', 'градуса')
        temperature = num2words(round(temperature), lang='ru')

        morph = pymorphy2.MorphAnalyzer(lang='ru')
        words_city = city.split()
        for i in range(len(words_city)):
            words_city[i] = morph.parse(words_city[i])[0].inflect({'masc', 'loct'}).word

        city = ' '.join(words_city)

        say(f'Температура в {city} сейчас {temperature} {degree_word}, {forecast}.', speak_model_ru)
    except Exception:
        say("Похоже город неверный!", speak_model_ru)


def search_person_vk(speak_model_ru, speak_model_en=None):
    name = listen().split()

    if not name:
        say("Имя для поиска не указано.", speak_model_ru)
        return

    formatted_name = " ".join(part.capitalize() for part in name)
    vk_search_term_encoded = urllib.parse.quote(formatted_name)
    vk_url = "https://vk.com/people/" + vk_search_term_encoded
    webbrowser.get().open(vk_url)
    say("Поиск в социальной сети ВКонтакте выполнен.", speak_model_ru)


def say(text, speak_model_ru):

    start = time.time()
    audio = speak_model_ru.apply_tts(text=text,
                            speaker='xenia',
                            sample_rate=48000)
    end = time.time()
    print(end - start)

    sd.play(audio, 48000)
    time.sleep(len(audio) / 48000 + 0.2)
    sd.stop()

def say_english(text, speak_model_en):

    start = time.time()
    audio = speak_model_en.apply_tts(text=text,
                                  speaker='en_0',
                                  sample_rate=48000)
    end = time.time()
    print(end - start)

    sd.play(audio, 48000)
    time.sleep(len(audio) / 48000 + 0.2)
    sd.stop()


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
                return data

def recognise(speak_model_ru, speak_model_en,  model, tokenizer, lbl_encoder):
    while True:
        text = listen()
        print(text)

        trg = bi.triggers.intersection(text.split())
        if not trg:
            continue

        text.replace(list(trg)[0], '')

        with open("../voice_assistant_data/intents.json", encoding='utf-8') as file:
            data = json.load(file)

        max_len = 20
        result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([text]),
                                                                          truncating='post', maxlen=max_len))

        # вероятность распознавания - то, что фраза реально подходит под pattern
        max_arg = np.argmax(result)

        # Получение tag
        tag = lbl_encoder.inverse_transform([max_arg])

        # Получение вероятности предсказания для наиболее вероятного класса
        predicted_probability = result[0][max_arg]
        print(predicted_probability)

        # Определение порогового значения
        threshold = 0.902

        # Если вероятность предсказания выше порогового значения, считаем его достоверным
        if predicted_probability > threshold:
            for i in data['intents']:
                if i['tag'] == tag:
                    parts = i['tag'].split(' ')
                    state = parts[0]
                    function = parts[1]
                    if state == 'active':
                        say(random.choice(i['responses']), speak_model_ru)
                        # Дописать везде ru у русской модели
                        # Дописать везде speak_model_en = None как парамтр по умолчанию
                        exec(function + '(speak_model_ru, speak_model_en)')
                    else:
                        say(random.choice(i['responses']), speak_model_ru)
        else:
            say("К сожалению, я пока не знаю, что вам ответить.", speak_model_ru)
