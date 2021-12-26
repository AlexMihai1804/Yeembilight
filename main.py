from bulb_yeelight import BulbYeelight
import pyautogui
import time
import os
from yeelight import Bulb
from tkinter import *
from tkinter import messagebox
import threading

bulbs = []
rate = 60 / 144
run = False


# 0-WHOLE SCREEN
# 1-TOP 2-LEFT 3-BOTTOM 4-RIGHT
# 5-TOP-CENTRE 6-LEFT-CENTRE 7-BOTTOM-CENTRE 8-RIGHT-CENTRE
# 9-CORNER-TOP-LEFT 10-CORNER-BOTTOM-LEFT 11-CORNER-BOTTOM-RIGHT 12-CORNER-TOP-RIGHT

def position_int_to_string(pos):
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
    return pos


def position_string_to_int(pos):
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
    return pos


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


def get_screenshot():
    scr = pyautogui.screenshot().resize((3, 3))
    return scr


def load():
    def file_load():
        is_ok = True
        if os.path.isfile('config.txt'):
            file = open('config.txt', 'r')
            lines = file.readlines()
            file.close()
            lines.pop(0)
            for line in lines:
                k1 = line.find(' ')
                k2 = line.rfind(' ')
                position = int(line[0:k1])
                ip = str(line[k1 + 1:k2])
                bright = int(line[k2 + 1:])
                error = False
                try:
                    Bulb(ip).get_properties()
                except:
                    is_ok = False
                    error = True
                if not error:
                    bulbs.append((position, BulbYeelight(ip), ip, bright))
        else:
            messagebox.showinfo(title='Config file created',
                                message='No config file detected!\nCreated configuration file')
            file = open('config.txt', 'w')
            file.write("Configuration file\n")
            file.close()
        return is_ok

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
        file.write(str(x[0]) + ' ' + x[2] + ' ' + str(x[3]) + '\n')
    file.close()


def modify_configuration():
    def exit_from_config():
        configuration_window.destroy()
        start_button['state'] = NORMAL
        config_button['state'] = NORMAL
        exit_button['state'] = NORMAL

    global configuration_window
    global bulb_list
    global start_button
    global config_button
    global exit_button
    global icon
    start_button['state'] = DISABLED
    config_button['state'] = DISABLED
    exit_button['state'] = DISABLED
    configuration_window = Tk()
    configuration_window.resizable(False, False)
    configuration_window.title("Edit Configuration")
    configuration_window.iconphoto(True, icon)
    bulb_list = Listbox(configuration_window, font=("Arial", 12), width=50, height=14)
    bulb_list.grid(row=0, rowspan=5, column=0)
    show_bulbs()
    add_bulb_button = Button(configuration_window, text="Add new bulb manual", command=add_bulb, font=("Arial", 20),
                             width=17)
    add_bulb_button.grid(row=1, column=1)
    add_bulb_auto_button = Button(configuration_window, text="Add new bulb auto", command=add_bulb_auto,
                                  font=("Arial", 20), width=17)
    add_bulb_auto_button.grid(row=0, column=1)
    edit_bulb_button = Button(configuration_window, text="Edit selected bulb", command=edit_bulb, font=("Arial", 20),
                              width=17)
    edit_bulb_button.grid(row=2, column=1)
    del_bulb_button = Button(configuration_window, text="Delete selected bulb", command=del_bulb, font=("Arial", 20),
                             width=17)
    del_bulb_button.grid(row=3, column=1)
    exit_button_config = Button(configuration_window, text="Exit", command=exit_from_config,
                                font=("Arial", 20), width=17)
    exit_button_config.grid(row=4, column=1)
    configuration_window.protocol("WM_DELETE_WINDOW", exit_from_config)
    configuration_window.mainloop()


def add_bulb_auto():
    bulb_ips = []

    def auto_discover():
        def try_ip(ip):
            try:
                Bulb(ip).get_properties()
                new_bulb = True
                for x in bulbs:
                    if x[2] == ip:
                        new_bulb = False
                        break
                if new_bulb:
                    bulb_ips.append(ip)
                    discovered_bulbs_list.insert(discovered_bulbs_list.size(), ip)
            except:
                pass

        for i in range(2):
            for j in range(256):
                ip = "192.168." + str(i) + '.' + str(j)
                x = threading.Thread(target=try_ip, args=(ip,))
                x.start()

    def add_bulb_in_list():
        try:
            k = int(discovered_bulbs_list.curselection()[0])
            bulbs.append((position_string_to_int(position_input.get()), Bulb(bulb_ips[k - 1]), bulb_ips[k - 1],
                          int(brightness_slider.get())))
            save_configuration_to_file()
            auto_add_window.destroy()
            modify_configuration()
        except:
            messagebox.showerror(title='ERROR!', message='You need to select a bulb in order to add it')

    def exit_from_add():
        global start_button
        global config_button
        global exit_button
        start_button['state'] = NORMAL
        config_button['state'] = NORMAL
        exit_button['state'] = NORMAL
        auto_add_window.destroy()

    global configuration_window
    global icon
    configuration_window.destroy()
    auto_add_window = Tk()
    auto_add_window.resizable(False, False)
    auto_add_window.title("Auto add bulbs")
    auto_add_window.iconphoto(True, icon)
    discovered_bulbs_list = Listbox(auto_add_window, font=("Arial", 12), width=50, height=12)
    discovered_bulbs_list.grid(row=0, rowspan=5, column=0)
    auto_discover()
    position_text = Label(auto_add_window, text="Select bulb's position", font=("Arial", 20))
    position_text.grid(column=1, row=0, columnspan=2)
    position_input = StringVar(auto_add_window)
    position_input.set("WHOLE SCREEN")
    position_option_menu = OptionMenu(auto_add_window, position_input, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM", "RIGHT",
                                      "TOP-CENTRE",
                                      "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE", "CORNER-TOP-LEFT", "LEFT-CENTRE",
                                      "CORNER-BOTTOM-RIGHT", "CORNER-TOP-RIGHT")
    position_option_menu.config(font=("Arial", 15), width=30, height=1)
    position_option_menu.grid(column=1, row=1, columnspan=2)
    brightness_text = Label(auto_add_window, text="Select bulb's brightness", font=("Arial", 20))
    brightness_text.grid(column=1, row=2, columnspan=2)
    brightness_slider = Scale(auto_add_window, from_=100, to=0, orient=HORIZONTAL, tickinterval=10, resolution=10,
                              font=("Arial", 10), length=350)
    brightness_slider.set(100)
    brightness_slider.grid(column=1, row=3, columnspan=2)
    add_button = Button(auto_add_window, text="Add", command=add_bulb_in_list, font=("Arial", 20), width=10)
    add_button.grid(column=1, row=4)
    exit_add = Button(auto_add_window, text="Exit", command=exit_from_add, font=("Arial", 20), width=10)
    exit_add.grid(column=2, row=4)
    auto_add_window.protocol("WM_DELETE_WINDOW", exit_from_add)
    auto_add_window.mainloop()


def edit_bulb():
    global bulb_list
    global add_bulb_window
    global configuration_window
    global position_change
    global icon

    def save_edit():
        pos, bulb, ip, bright = bulbs[k]
        pos = position_string_to_int(str(position_change.get()))
        bright = int(brightness_slider.get())
        bulbs[k] = (pos, bulb, ip, bright)
        save_configuration_to_file()
        edit_window.destroy()
        modify_configuration()

    def exit_edit():
        global start_button
        global config_button
        global exit_button
        start_button['state'] = NORMAL
        config_button['state'] = NORMAL
        exit_button['state'] = NORMAL
        edit_window.destroy()

    try:
        k = int(bulb_list.curselection()[0])
        configuration_window.destroy()
        edit_window = Tk()
        edit_window.resizable(False, False)
        edit_window.title("Edit bulb's info")
        edit_window.iconphoto(True, icon)
        position_text = Label(edit_window, text="Select bulb's position", font=("Arial", 20))
        position_text.pack()
        position_change = StringVar(edit_window)
        position_change.set(position_int_to_string(bulbs[k][0]))
        position_option_menu = OptionMenu(edit_window, position_change, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM",
                                          "RIGHT",
                                          "TOP-CENTRE",
                                          "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE", "CORNER-TOP-LEFT",
                                          "LEFT-CENTRE",
                                          "CORNER-BOTTOM-RIGHT", "CORNER-TOP-RIGHT")
        position_option_menu.config(font=("Arial", 15), width=30, height=1)
        position_option_menu.pack()
        brightness_text = Label(edit_window, text="Select bulb's brightness", font=("Arial", 20))
        brightness_text.pack()
        brightness_slider = Scale(edit_window, from_=100, to=0, orient=HORIZONTAL, tickinterval=10, resolution=10,
                                  font=("Arial", 10), length=350)
        brightness_slider.set(bulbs[k][3])
        brightness_slider.pack()
        done_button = Button(edit_window, text="Save current settings", command=save_edit, font=("Arial", 20), width=22)
        done_button.pack()
        exit_button = Button(edit_window, text="Exit", command=exit_edit, font=("Arial", 20), width=22)
        exit_button.pack()
        edit_window.protocol("WM_DELETE_WINDOW", exit_edit)
        edit_window.mainloop()
    except:
        messagebox.showerror(title='ERROR!', message='You need to select a bulb in order to edit')


def add_bulb():
    def add_bulb_in_list():
        ip = str(ip_entry_box.get())
        pos = str(position_input.get())
        pos = position_string_to_int(pos)
        bright = int(brightness_slider.get())
        error = False
        try:
            Bulb(ip).get_properties()
        except:
            error = True
            messagebox.showerror(title='ERROR!', message='Wrong ip or bulb is offline')
        if not error:
            bulbs.append((pos, BulbYeelight(ip), ip, bright))
            file = open('config.txt', 'a')
            file.write(str(pos) + ' ' + ip + ' ' + str(bright) + '\n')
            add_bulb_window.destroy()
            modify_configuration()

    def exit_from_add():
        global start_button
        global config_button
        global exit_button
        start_button['state'] = NORMAL
        config_button['state'] = NORMAL
        exit_button['state'] = NORMAL
        add_bulb_window.destroy()

    global position_input
    global ip_entry_box
    global add_bulb_window
    global configuration_window
    global icon
    configuration_window.destroy()
    add_bulb_window = Tk()
    add_bulb_window.resizable(False, False)
    add_bulb_window.title("Add a new bulb")
    add_bulb_window.iconphoto(True, icon)
    position_text = Label(add_bulb_window, text="Select bulb's position", font=("Arial", 20))
    position_text.grid(column=0, row=0)
    position_input = StringVar(add_bulb_window)
    position_input.set("WHOLE SCREEN")
    position_option_menu = OptionMenu(add_bulb_window, position_input, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM", "RIGHT",
                                      "TOP-CENTRE",
                                      "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE", "CORNER-TOP-LEFT", "LEFT-CENTRE",
                                      "CORNER-BOTTOM-RIGHT", "CORNER-TOP-RIGHT")
    position_option_menu.config(font=("Arial", 15), width=30, height=1)
    position_option_menu.grid(column=0, row=1)
    info_text = Label(add_bulb_window, text="Enter bulb's ip", font=("Arial", 20))
    info_text.grid(column=0, row=2)
    ip_entry_box = Entry(add_bulb_window, font=("Arial", 20))
    ip_entry_box.grid(column=0, row=3)
    brightness_text = Label(add_bulb_window, text="Select bulb's brightness", font=("Arial", 20))
    brightness_text.grid(column=0, row=4)
    brightness_slider = Scale(add_bulb_window, from_=100, to=0, orient=HORIZONTAL, tickinterval=10, resolution=10,
                              font=("Arial", 10), length=350)
    brightness_slider.set(100)
    brightness_slider.grid(column=0, row=5)
    add_button = Button(add_bulb_window, text="Add", command=add_bulb_in_list, font=("Arial", 20), height=3, width=10)
    add_button.grid(column=1, row=0, rowspan=3)
    exit_add = Button(add_bulb_window, text="Exit", command=exit_from_add, font=("Arial", 20), height=3, width=10)
    exit_add.grid(column=1, row=4, rowspan=3)
    add_bulb_window.protocol("WM_DELETE_WINDOW", exit_from_add)
    add_bulb_window.mainloop()


def del_bulb():
    global bulb_list
    global add_bulb_window
    global configuration_window
    try:
        k = int(bulb_list.curselection()[0])
        configuration_window.destroy()
        bulbs.pop(k)
        save_configuration_to_file()
        modify_configuration()
    except:
        messagebox.showerror(title='ERROR!', message='You need to select a bulb in order to remove')


def show_bulbs():
    global bulb_list
    for x in range(len(bulbs)):
        pos = position_int_to_string(bulbs[x][0])
        bulb_list.insert(x + 1, pos + ' ' + bulbs[x][2] + " brightness " + str(bulbs[x][3]) + '%')


def start():
    global run
    run = not run
    global config_button
    global exit_button
    global start_button
    if run:
        t = threading.Thread(target=sync_with_bulbs)
        t.start()
        config_button['state'] = DISABLED
        exit_button['state'] = DISABLED
        start_button["text"] = "Stop"
    else:
        config_button['state'] = NORMAL
        exit_button['state'] = NORMAL
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
                brightness = bulbs[i][3]
                v1 = int(v * brightness / 100)
                bulbs[i][1].set_hsv(h, s, v1)
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
    def close_main_window():
        global main_window
        global run
        run = False
        main_window.destroy()


    global start_button
    global config_button
    global exit_button
    global main_window
    global icon
    load()
    main_window = Tk()
    main_window.resizable(False, False)
    main_window.title("Yeembilight")
    icon = PhotoImage(file="Logo2.png")
    main_window.iconphoto(True, icon)
    start_button = Button(main_window, text="Start", command=start, font=("Arial", 20), width=30)
    start_button.grid(row=0, column=0, columnspan=2)
    config_button = Button(main_window, text="Edit configuration", command=modify_configuration, font=("Arial", 20),
                           width=15)
    config_button.grid(row=1, column=0)
    exit_button = Button(main_window, text="Exit", command=main_window.destroy, font=("Arial", 20), width=15)
    exit_button.grid(row=1, column=1)
    main_window.protocol("WM_DELETE_WINDOW", close_main_window)
    main_window.mainloop()
