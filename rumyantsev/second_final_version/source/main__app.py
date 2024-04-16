import threading
import tkinter as tk
from voice_assistant.source.functions import recognise
import pickle
from tensorflow import keras

class App(tk.Tk):
    def __init__(self, model, tokenizer, lbl_encoder):
        super().__init__()
        #Инициализация полей для ИИ
        self.model = model
        self.tokenizer = tokenizer
        self.lbl_encoder = lbl_encoder

        self.title("Голосовой помощник Галя")
        self.geometry('600x500')
        self.resizable(False, False)
        self.configure(bg="pink")
        self.button = tk.Button(self,
                                command=self.start_action,
                                width=20,
                                height=5,
                                activeforeground="#FFFFFF",
                                activebackground="#22B14C",
                                text="Говорить")
        self.button.pack()
        self.button.place(relx=0.5, rely=0.5, anchor='center')

    def start_action(self):
        self.button.config(state=tk.DISABLED)
        self.button.config(text="Слушаю и выполняю")
        #click - лямбда-функция, которая работает с помощью обуцченной модели
        thread = threading.Thread(target=lambda: recognise(self.model, self.tokenizer, self.lbl_encoder))
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
    # load trained model
    model = keras.models.load_model('../neural_network/chat_model.keras')

    # load tokenizer object
    with open('../neural_network/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('../neural_network/label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    app = App(model, tokenizer, lbl_encoder)
    app.mainloop()

if __name__ == "__main__":
    main()



