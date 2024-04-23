import subprocess
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
from googletrans import Translator


# # для отправки письма
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# для таймера
import threading


class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""
    todo_list = []  # Создаем пустой список для хранения задач

    def create_todo_list(self):
        self.todo_list = []  # Очищаем список задач при создании нового списка
        play_voice_assistant_speech("Создан новый список дел.")

    def add_to_todo_list(self, task):
        self.todo_list.append(task)
        play_voice_assistant_speech(f"Задача '{task}' добавлена в список дел.")

    def remove_from_todo_list(self, task):
        if task in self.todo_list:
            self.todo_list.remove(task)
            play_voice_assistant_speech(f"Задача '{task}' удалена из списка дел.")
        else:
            play_voice_assistant_speech(f"Задачи '{task}' нет в списке дел.")

    def show_todo_list(self):
        if self.todo_list:
            tasks = ", ".join(self.todo_list)
            play_voice_assistant_speech(f"Список задач на сегодня: {tasks}.")
        else:
            play_voice_assistant_speech("Список задач пуст.")


def setup_voice():
    """
    Установка голоса по умолчанию
    """
    # Оставлю эту функцию здесь, но она пока что не нужнаы
    pass


def play_voice_assistant_speech(text_to_speech, lang='ru', tld='ru'):
    """
    Проигрывание речи ответов голосового ассистента
    """
    tts = gTTS(text=text_to_speech, lang=lang, tld=tld)
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
            return ""

        # Пытаемся выполнить онлайн распознавание
        try:
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        # # Если онлайн распознавание не удалось, пытаемся выполнить оффлайн распознавание
        # if not recognized_data:
        #     print("Онлайн распознавание не удалось, выполняю оффлайн распознавание...")
        #     recognized_data = offline_recognition()

    return recognized_data


# def offline_recognition():
#     """
#     Переключение на оффлайн-распознавание речи с использованием модели Vosk
#     """
#     # Устанавливаем уровень логирования для Vosk
#     SetLogLevel(0)
#
#     # Загружаем модель для русского языка
#     model = Model("path/to/vosk-model-small-ru-0.22")
#
#     # Создаем рекогнайзер
#     recognizer = KaldiRecognizer(model, 16000)
#
#     # Читаем аудиофайл и выполняем распознавание
#     with wave.open("microphone-results.wav", "rb") as wf:
#         # Считываем все данные из аудиофайла
#         data = wf.readframes(wf.getnframes())
#         if len(data) == 0:
#             return ""  # Возвращаем пустую строку, если аудиофайл пустой
#
#         # Передаем данные рекогнайзеру и получаем результат распознавания
#         recognizer.AcceptWaveform(data)
#
#         # Получаем и возвращаем результат распознавания
#         return recognizer.Result()


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
    Получает ответ на приветствие в соответствии с текущим временем суток
    или рандомный выбор из блока "get_greeting_response"
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


def send_email(email_config, config):
    email_address = email_config.get("email_address")
    email_subject = email_config.get("email_subject")
    email_message = email_config.get("email_message")

    # Получаем данные о отправителе из конфигурации
    sender_email = config["email_credentials"]["sender_email"]
    sender_password = config["email_credentials"]["sender_password"]

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_address
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_message, 'plain'))

    try:
        # Используем порт 465 и протокол SSL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email_address, text)
        server.quit()
        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")


def prompt_for_vk_search_query():
    """
    Запрашивает у пользователя имя и фамилию для поиска в ВКонтакте
    """
    play_voice_assistant_speech("Кого вы бы хотели найти в ВКонтакте?")
    name = audio_record_recognize().split()  # Разделение введенной строки на отдельные слова
    return name


def search_person_vk(name):
    """
    Поиск человека по базе данных социальной сети ВКонтакте
    """
    if not name:
        play_voice_assistant_speech("Имя для поиска не указано.")
        return

    formatted_name = " ".join(part.capitalize() for part in name)
    vk_search_term_encoded = urllib.parse.quote(formatted_name)
    vk_url = "https://vk.com/people/" + vk_search_term_encoded
    webbrowser.get().open(vk_url)
    play_voice_assistant_speech("Поиск в социальной сети ВКонтакте выполнен.")


def translate_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, src='ru', dest='en')
    return translated_text.text


def translate_to_russian(text):
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='ru')
    return translated_text.text


def search_recipe(query):
    """
    Поиск рецепта по запросу пользователя с помощью API The Meal DB
    """
    translated_query = translate_to_english(query)
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={translated_query}"
    response = requests.get(url)
    data = response.json()

    if data['meals']:
        meal = data['meals'][0]
        recipe_name = translate_to_russian(meal['strMeal'])
        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            if ingredient:
                ingredients.append(translate_to_russian(ingredient))
            else:
                break

        instructions = translate_to_russian(meal['strInstructions'])

        recipe_text = f"Рецепт блюда {recipe_name}:"
        recipe_text += "\n\nИнгредиенты:"
        for ingredient in ingredients:
            recipe_text += f"\n- {ingredient}"
        recipe_text += f"\n\nИнструкции по приготовлению:\n{instructions}"

        play_voice_assistant_speech(recipe_text)
    else:
        error_responses = [
            "К сожалению, я не смог найти рецепт для этого блюда.",
            "Извините, я не знаю, как готовить это блюдо.",
            "Мне кажется, я не знаю рецепта для этого блюда.",
            "Похоже, я не могу найти информацию о рецепте для этого блюда."
        ]
        play_voice_assistant_speech(random.choice(error_responses))


def toss_coin():
    """
    Подбрасывание монетки после запроса стороны у пользователя
    """
    play_voice_assistant_speech("Выберите сторону: орёл или решка.")
    user_choice = audio_record_recognize()
    user_choice = user_choice.lower()

    while user_choice not in ["орёл", "решка"]:
        play_voice_assistant_speech("Пожалуйста, выберите только 'орёл' или 'решка'.")
        user_choice = audio_record_recognize()
        user_choice = user_choice.lower()

    coin_side = random.choice(["орёл", "решка"])

    if user_choice == coin_side:
        result = "Вы победили! "
    else:
        result = "Вы проиграли. "

    return result + f"Монета выпала на {coin_side}."


def record_voice_to_text(filename):
    """
    Запись голосового ввода пользователя в текстовый файл
    """
    play_voice_assistant_speech("Пожалуйста, скажите текст для записи в файл.")
    user_input = audio_record_recognize()

    if user_input:
        with open(filename, "a") as file:
            # Проверяем, существует ли файл, если нет, то создаем его
            if not os.path.exists(filename):
                file.write("Голосовая запись:\n")
            file.write(user_input + "\n")
        play_voice_assistant_speech("Текст успешно записан в файл.")
    else:
        play_voice_assistant_speech("Не удалось распознать речь. Попробуйте еще раз.")


def set_timer(seconds):
    """
    Установка таймера на определенное количество секунд
    """
    def timer_complete():
        play_voice_assistant_speech("Время вышло!")

    # Создаем таймер с указанным временем
    timer = threading.Timer(seconds, timer_complete)
    timer.start()
    play_voice_assistant_speech(f"Таймер установлен на {seconds} секунд.")


def handle_intent(intent, config, assistant):
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
            play_voice_assistant_speech(random.choice(responses))
            play_voice_assistant_speech(f"{current_time}")
        elif intent == "current_date":
            if "какая сегодня дата" in examples:
                current_date = get_current_date("full_date")
            play_voice_assistant_speech(random.choice(responses))
            play_voice_assistant_speech(current_date)
        elif intent == "send_email":
            play_voice_assistant_speech(random.choice(responses))
            send_email(config["intents"][intent], config)
        elif intent == "to_do_list_create":
            assistant.create_todo_list()
        elif intent == "to_do_list_add":
            play_voice_assistant_speech(random.choice(responses))
            user_input = audio_record_recognize()
            assistant.add_to_todo_list(user_input)
        elif intent == "to_do_list_remove":
            play_voice_assistant_speech(random.choice(responses))
            user_input = audio_record_recognize()
            assistant.remove_from_todo_list(user_input)
        elif intent == "to_do_list_show":
            assistant.show_todo_list()
        elif intent == "recipe_search":
            play_voice_assistant_speech(random.choice(responses))
            user_query = audio_record_recognize()
            search_recipe(user_query)
        elif intent == "search_person_vk":
            play_voice_assistant_speech(random.choice(responses))
            name = prompt_for_vk_search_query()
            search_person_vk(name)
        elif intent == "toss_coin":
            play_voice_assistant_speech(random.choice(responses))
            result = toss_coin()
            play_voice_assistant_speech(result)
        elif intent == "record_to_file":
            play_voice_assistant_speech(random.choice(responses))
            record_voice_to_text("recorded_text.txt")
        elif intent == "set_timer":
            play_voice_assistant_speech(random.choice(responses))
            play_voice_assistant_speech("На сколько секунд установить таймер?")
            user_input = audio_record_recognize()
            try:
                seconds = int(user_input)
                set_timer(seconds)
            except ValueError:
                play_voice_assistant_speech("Пожалуйста, укажите число секунд для таймера.")

    else:
        play_voice_assistant_speech(config["failure_phrases"])


def main():

    with open("config.json", "r") as file:
        config = json.load(file)

    assistant = VoiceAssistant()

    try:
        while True:
            voice_input = audio_record_recognize()
            print("Вы сказали:", voice_input)

            for intent, data in config["intents"].items():
                for example in data["examples"]:
                    if example in voice_input:
                        handle_intent(intent, config, assistant)
                        break
    finally:
        # Удаляем файл microphone-results.wav по завершении работы программы
        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")


if __name__ == "__main__":
    main()

