from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import threading
import tkinter as tk
from functions import click
import data_set

class App(tk.Tk):
    def __init__(self, vectorizer, clf):
        super().__init__()
        #Инициализация полей для ИИ
        self.vectorizer = vectorizer
        self.clf = clf

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
        thread = threading.Thread(target=lambda: click(self.vectorizer, self.clf))
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
    # Работа ИИ
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(data_set.data_set.keys()))
    clf = LogisticRegression()
    clf.fit(vectors, list(data_set.data_set.values()))
    del data_set.data_set

    app = App(vectorizer, clf)
    app.mainloop()

if __name__ == "__main__":
    main()



