from bulb_yeelight import BulbYeelight
import pyautogui
import time
import os
from yeelight import Bulb
from tkinter import *
from tkinter import messagebox
import threading
import tkinter as tk

bulbs = []
rate = 60 / 144
run = False


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    h = None
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df / mx) * 100
    v = mx * 100
    return h, s, v


# 0-WHOLE SCREEN
# 1-TOP 2-LEFT 3-BOTTOM 4-RIGHT
# 5-TOP-CENTRE 6-LEFT-CENTRE 7-BOTTOM-CENTRE 8-RIGHT-CENTRE
# 9-CORNER-TOP-LEFT 10-CORNER-BOTTOM-LEFT 11-CORNER-BOTTOM-RIGHT 12-CORNER-TOP-RIGHT


def determine_hsv(scr, position):
    r = 0
    g = 0
    b = 0
    if position == 0:
        for x in range(0, 3):
            for y in range(0, 3):
                k, i, j = scr.getpixel((x, y))
                r += k
                g += i
                b += j
        r = int(r / 9)
        g = int(g / 9)
        b = int(b / 9)
    elif position == 1:
        for x in range(0, 3):
            k, i, j = scr.getpixel((0, x))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 2:
        for x in range(0, 3):
            k, i, j = scr.getpixel((x, 0))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 3:
        for x in range(0, 3):
            k, i, j = scr.getpixel((2, x))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 4:
        for x in range(0, 3):
            k, i, j = scr.getpixel((x, 2))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 5:
        r, g, b = scr.getpixel((0, 1))
    elif position == 6:
        r, g, b = scr.getpixel((1, 0))
    elif position == 7:
        r, g, b = scr.getpixel((2, 1))
    elif position == 8:
        r, g, b = scr.getpixel((1, 2))
    elif position == 9:
        r, g, b = scr.getpixel((0, 0))
    elif position == 10:
        r, g, b = scr.getpixel((2, 0))
    elif position == 11:
        r, g, b = scr.getpixel((2, 2))
    elif position == 12:
        r, g, b = scr.getpixel((0, 2))
    h, s, v = rgb_to_hsv(r, g, b)
    return h, s, v


def get_screenshot():
    scr = pyautogui.screenshot().resize((3, 3))
    return scr


def file_load():
    ok = True
    if os.path.isfile('config.txt'):
        file = open('config.txt', 'r')
        lines = file.readlines()
        file.close()
        for x in range(1, len(lines)):
            line = str(lines[x])
            ip = None
            position = None
            error = False
            if line[1] == ' ':
                position = int(line[0])
                ip = line[2:-1]
            elif line[2] == ' ':
                position = int(line[0]) * 10 + int(line[1])
                ip = line[3:-1]
            try:
                Bulb(ip).get_properties()
            except:
                ok = False
                error = True
                print(position)
            if not error:
                bulbs.append((position, BulbYeelight(ip), ip))
            else:
                print(ip)
    else:
        messagebox.showinfo(title='Config file created', message='No config file detected!\nCreated configuration file')
        file = open('config.txt', 'w')
        file.write("Configuration file\n")
        file.close()
    return ok


def load():
    ok = file_load()
    while not ok:
        if messagebox.askretrycancel(title="Load error", message="Some bulbs can't be loaded\nMAKE SURE IS POWERED ON "
                                                                 "AND CONNECTED TO WIFI AND THEN TRY AGAIN\nRetry-try"
                                                                 " again Cancel-Continue with loaded bulbs"):
            while len(bulbs) > 0:
                bulbs.pop()
            ok = file_load()
        else:
            save_configuration_to_file()
            ok = True


def save_configuration_to_file():
    file = open('config.txt', 'w')
    file.write("Configuration file\n")
    for x in bulbs:
        file.write(str(x[0]) + ' ' + x[2] + '\n')
    file.close()


def modify_configuration():
    global configuration_window
    global bulb_list
    global start_button
    global config_button
    global exit_button
    global add_bulb_button
    global del_bulb_button
    global exit_button_config
    start_button['state'] = tk.DISABLED
    config_button['state'] = tk.DISABLED
    exit_button['state'] = tk.DISABLED
    configuration_window = Tk()
    configuration_window.resizable(False, False)
    configuration_window.title("Edit Configuration")
    bulb_list = Listbox(configuration_window, font=("Arial", 12), width=35, height=8)
    bulb_list.grid(row=0, rowspan=3, column=0)
    show_bulbs()
    add_bulb_button = Button(configuration_window, text="Add new bulb", command=add_bulb, font=("Arial", 20), width=17)
    add_bulb_button.grid(row=0, column=1)
    del_bulb_button = Button(configuration_window, text="Delete selected bulb", command=del_bulb, font=("Arial", 20),
                             width=17)
    del_bulb_button.grid(row=1, column=1)
    exit_button_config = Button(configuration_window, text="Exit", command=exit_from_config,
                                font=("Arial", 20), width=17)
    exit_button_config.grid(row=2, column=1)
    configuration_window.mainloop()


def exit_from_config():
    global configuration_window
    global start_button
    global config_button
    global exit_button
    configuration_window.destroy()
    start_button['state'] = tk.NORMAL
    config_button['state'] = tk.NORMAL
    exit_button['state'] = tk.NORMAL


def exit_from_add():
    global start_button
    global config_button
    global exit_button
    global add_bulb_window
    start_button['state'] = tk.NORMAL
    config_button['state'] = tk.NORMAL
    exit_button['state'] = tk.NORMAL
    add_bulb_window.destroy()


def add_bulb_in_list():
    global position_input
    global ip_entry_box
    global add_bulb_window
    ip = str(ip_entry_box.get())
    pos = str(position_input.get())
    if pos == "WHOLE SCREEN":
        pos = 0
    elif pos == "TOP":
        pos = 1
    elif pos == "LEFT":
        pos = 2
    elif pos == "BOTTOM":
        pos = 3
    elif pos == "RIGHT":
        pos = 4
    elif pos == "TOP-CENTRE":
        pos = 5
    elif pos == "LEFT-CENTRE":
        pos = 6
    elif pos == "BOTTOM-CENTRE":
        pos = 7
    elif pos == "RIGHT-CENTRE":
        pos = 8
    elif pos == "CORNER-TOP-LEFT":
        pos = 9
    elif pos == "CORNER-BOTTOM-LEFT":
        pos = 10
    elif pos == "CORNER-BOTTOM-RIGHT":
        pos = 11
    elif pos == "CORNER-TOP-RIGHT":
        pos = 12
    error = False
    try:
        Bulb(ip).get_properties()
    except:
        error = True
        messagebox.showerror(title='ERROR!', message='Wrong ip or bulb is offline')
    if not error:
        bulbs.append((pos, BulbYeelight(ip), ip))
        file = open('config.txt', 'a')
        file.write(str(pos) + ' ' + ip + '\n')
        add_bulb_window.destroy()
        modify_configuration()


def add_bulb():
    global position_input
    global ip_entry_box
    global add_bulb_window
    global configuration_window
    global add_bulb_window
    configuration_window.destroy()
    add_bulb_window = Tk()
    add_bulb_window.resizable(False, False)
    add_bulb_window.title("Add a new bulb")
    position_input = StringVar(add_bulb_window)
    position_input.set("WHOLE SCREEN")
    position_option_menu = OptionMenu(add_bulb_window, position_input, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM", "RIGHT",
                                      "TOP-CENTRE",
                                      "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE", "CORNER-TOP-LEFT", "LEFT-CENTRE",
                                      "CORNER-BOTTOM-RIGHT", "CORNER-TOP-RIGHT")
    position_option_menu.config(font=("Arial", 15), width=30, height=1)
    position_option_menu.grid(column=0, row=0)
    info_text = Label(add_bulb_window, text="Enter bulb's ip", font=("Arial", 20))
    info_text.grid(column=0, row=1)
    ip_entry_box = Entry(add_bulb_window, font=("Arial", 20))
    ip_entry_box.grid(column=0, row=2)
    add_button = Button(add_bulb_window, text="Add", command=add_bulb_in_list, font=("Arial", 20), height=2, width=10)
    add_button.grid(column=1, row=0, rowspan=2)
    exit_add = Button(add_bulb_window, text="Exit", command=exit_from_add, font=("Arial", 20), width=10)
    exit_add.grid(column=1, row=2)
    add_bulb_window.mainloop()


def del_bulb():
    global bulb_list
    global add_bulb_window
    global configuration_window
    try:
        k = int(bulb_list.curselection()[0])
        configuration_window.destroy()
        bulbs.pop(k)
        print(len(bulbs))
        save_configuration_to_file()
        modify_configuration()
    except:
        messagebox.showerror(title='ERROR!', message='You need to select a bulb in order to remove')


def show_bulbs():
    global bulb_list
    for x in range(len(bulbs)):
        pos = bulbs[x][0]
        if pos == 0:
            pos = "WHOLE SCREEN"
        elif pos == 1:
            pos = "TOP"
        elif pos == 2:
            pos = "LEFT"
        elif pos == 3:
            pos = "BOTTOM"
        elif pos == 4:
            pos = "RIGHT"
        elif pos == 5:
            pos = "TOP-CENTRE"
        elif pos == 6:
            pos = "LEFT-CENTRE"
        elif pos == 7:
            pos = "BOTTOM-CENTRE"
        elif pos == 8:
            pos = "RIGHT-CENTRE"
        elif pos == 9:
            pos = "CORNER-TOP-LEFT"
        elif pos == 10:
            pos = "CORNER-BOTTOM-LEFT"
        elif pos == 11:
            pos = "CORNER-BOTTOM-RIGHT"
        elif pos == 12:
            pos = "CORNER-TOP-RIGHT"
        bulb_list.insert(x + 1, pos + ' ' + bulbs[x][2])


def start():
    global run
    run = not run
    global config_button
    global exit_button
    global start_button
    if run:
        t = threading.Thread(target=sync_with_bulbs)
        t.start()
        config_button['state'] = tk.DISABLED
        exit_button['state'] = tk.DISABLED
        start_button["text"] = "Stop"
    else:
        config_button['state'] = tk.NORMAL
        exit_button['state'] = tk.NORMAL
        start_button["text"] = "Start"


def sync_with_bulbs():
    bulbs.sort()
    for x in bulbs:
        x[1].initial_state()
    time.sleep(rate)
    time_after = float(time.time())
    while run:
        scr = get_screenshot()
        time_before = float(time.time())
        i = 0
        while i < len(bulbs):
            k = bulbs[i][0]
            h, s, v = determine_hsv(scr, k)
            while bulbs[i][0] == k:
                bulbs[i][1].set_hsv(h, s, v)
                i += 1
                if i == len(bulbs):
                    break
        time_since_last = time_before - time_after
        if time_since_last < rate:
            time.sleep(rate - time_since_last)
        time_after = float(time.time())
    for x in bulbs:
        x[1].revert_to_initial()


if __name__ == "__main__":
    global start_button
    global config_button
    global exit_button
    load()
    main_window = Tk()
    main_window.resizable(False, False)
    main_window.title("Yeembilight")
    start_button = Button(main_window, text="Start", command=start, font=("Arial", 20), width=30)
    start_button.grid(row=0, column=0, columnspan=2)
    config_button = Button(main_window, text="Edit configuration", command=modify_configuration, font=("Arial", 20),
                           width=15)
    config_button.grid(row=1, column=0)
    exit_button = Button(main_window, text="Exit", command=main_window.destroy, font=("Arial", 20), width=15)
    exit_button.grid(row=1, column=1)
    main_window.mainloop()
