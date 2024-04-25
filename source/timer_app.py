import tkinter

class timer_app():
    def __init__(self):
        pass

    def start_action(self):
        pass

    def check_thread(self):
        pass
    win = tkinter.Tk()
    win.geometry('400x300')
    win.resizable(False, False)

    win.config(bg='burlywood1')

    sec = tkinter.StringVar()
    tkinter.Entry(win, textvariable=sec, width=2, font='Helvetica 14').place(x=220, y=120)
    sec.set('00')
    mins = tkinter.StringVar()
    tkinter.Entry(win, textvariable=mins, width=2, font='Helvetica14').place(x=180, y=120)
    mins.set('00')
    hrs = tkinter.StringVar()
    tkinter.Entry(win, textvariable=hrs, width=2, font='Helvetica 14').place(x=142, y=120)
    hrs.set('00')

    tkinter.Label(win,
                  font=('Helvetica bold', 22),
                  text='Set the Timer',
                  bg='burlywood1').place(x=105, y=70)

    tkinter.Button(win, text='START',
                   bd='2',
                   bg='IndianRed1',
                   font=('Helveticabold', 10),
                   command=countdowntimer).place(x=167, y=165)
    thread = threading.Thread(win.mainloop())
    thread.start()