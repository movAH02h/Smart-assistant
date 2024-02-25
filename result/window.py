import tkinter as tk
from PIL import ImageTk
from functions import click

def __init_window__():
    window = tk.Tk()
    window.title("Голосовой помощник Галя")
    window.geometry('600x500')
    window.resizable(False, False)
    window.configure(bg="pink")

    #button initialization
    img = ImageTk.PhotoImage(file="images\\button.png")
    button = tk.Button(text="Галя", image=img, command=click)
    button.pack()
    button.place(relx=0.5, rely=0.5, anchor='center')
    window.mainloop()