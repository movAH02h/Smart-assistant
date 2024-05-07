import threading
import tkinter as tk
from source.functions import recognise
import pickle
from tensorflow import keras
import torch
import os

class main_app(tk.Tk):
    def __init__(self, model, tokenizer, lbl_encoder, speak_model_ru, speak_model_en):
        super().__init__()
        # Инициализация полей для ИИ
        self.model = model
        self.tokenizer = tokenizer
        self.lbl_encoder = lbl_encoder
        self.speak_model_ru = speak_model_ru
        self.speak_model_en = speak_model_en

        self.title("Голосовой помощник Галя")
        self.geometry('600x500')
        self.resizable(False, False)

        # Создаем холст Canvas вместо фона
        self.canvas = tk.Canvas(self, width=600, height=500)
        self.canvas.pack()

        # Загрузка изображения и добавление его на холст
        self.bg_image = tk.PhotoImage(file="../images/background.png")
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        self.logo = tk.PhotoImage(file="../images/new_logo.png")  # Загрузка логотипа изображения
        self.logo_label = tk.Label(self, image=self.logo)  # Создание метки для логотипа
        self.logo_label.pack()
        self.logo_label.place(relx=0.5, rely=0.3, anchor='center')

        self.button = tk.Button(self,
                                command=self.start_action,
                                width=20,
                                height=5,
                                activeforeground="#FFFFFF",
                                activebackground="#C0C0C0",
                                text="Говорить",
                                bg="#C0C0C0",  # Изменение цвета кнопки
                                fg="#FFFFFF",  # Изменение цвета текста кнопки
                                font=("Helvetica", 15, "bold"))  # Изменение шрифта кнопки
        self.button.pack()
        self.button.place(relx=0.5, rely=0.7, anchor='center')

    def start_action(self):
        self.button.config(state=tk.DISABLED)
        self.button.config(text="Слушаю и выполняю")
        # click - лямбда-функция, которая работает с помощью обученной модели
        thread = threading.Thread(target=lambda: recognise(self.speak_model_ru, self.speak_model_en,  self.model, self.tokenizer, self.lbl_encoder))
        thread.start()
        self.check_thread(thread)

    def check_thread(self, thread):
        if thread.is_alive():
            # используется именно lambda функция, потому что нам надо передать функцию как аргумент.
            # Т.к она должна вызваться после задержки
            # если не использовать lambda, то функция уйдет в рекурсию и выпадет ошибка
            # https://stacktuts.com/how-to-use-after-method-in-tkinter - сайт с объяснением
            self.after(100, lambda: self.check_thread(thread))
        else:
            self.button.config(state=tk.NORMAL, text="Говорить")

def main():
    # load speaking model
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file_ru = 'model_ru.pt'
    local_file_en = 'model_en.pt'

    if not os.path.isfile(local_file_ru):
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v4_ru.pt',
                                       local_file_ru)

    if not os.path.isfile(local_file_en):
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt',
                                       local_file_en)

    # Загрузка существующей модели русского языка - если есть на компьютере
    speak_model_ru = torch.package.PackageImporter(local_file_ru).load_pickle("tts_models", "model")
    speak_model_ru.to(device)

    # загркзка существующей модели английского языка
    speak_model_en = torch.package.PackageImporter(local_file_en).load_pickle("tts_models", "model")
    speak_model_en.to(device)

    # load trained model
    model = keras.models.load_model('../neural_network/chat_model.keras')

    # load tokenizer object
    with open('../neural_network/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('../neural_network/label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    app = main_app(model, tokenizer, lbl_encoder, speak_model_ru, speak_model_en)
    app.mainloop()

if __name__ == "__main__":
    main()
