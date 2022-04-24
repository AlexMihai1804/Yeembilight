import os
import threading
import time
from tkinter import *
from tkinter import messagebox

import ifaddr
from PIL import ImageGrab, ImageChops, Image
from yeelight import Bulb
from yeelight import discover_bulbs

from bulb_yeelight import BulbYeelight

bulbs = []
rate = 900
run = False
bar_correction = True
bbox = None


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
            k, i, j = scr.getpixel((x, 0))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 2:
        for x in range(0, 3):
            k, i, j = scr.getpixel((0, x))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 3:
        for x in range(0, 3):
            k, i, j = scr.getpixel((x, 2))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 4:
        for x in range(0, 3):
            k, i, j = scr.getpixel((2, x))
            r += k
            g += i
            b += j
        r = int(r / 3)
        g = int(g / 3)
        b = int(b / 3)
    elif position == 5:
        r, g, b = scr.getpixel((1, 0))
    elif position == 6:
        r, g, b = scr.getpixel((0, 1))
    elif position == 7:
        r, g, b = scr.getpixel((1, 2))
    elif position == 8:
        r, g, b = scr.getpixel((2, 1))
    elif position == 9:
        r, g, b = scr.getpixel((0, 0))
    elif position == 10:
        r, g, b = scr.getpixel((0, 2))
    elif position == 11:
        r, g, b = scr.getpixel((2, 2))
    elif position == 12:
        r, g, b = scr.getpixel((2, 0))
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


def get_screenshot(c):
    def trim(im):
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        return diff.getbbox()

    global bar_correction
    global bbox
    scr = ImageGrab.grab().resize((120, 120))
    if c == 0 and bar_correction is True:
        bbox = trim(scr)
    if bbox is None or bar_correction is False:
        return scr.resize((3, 3))
    else:
        return scr.crop(bbox).resize((3, 3))


def load():
    def file_load():
        global is_ok
        is_ok = True

        def load_line(line):
            global is_ok
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

        if os.path.isfile('config.txt'):
            file = open('config.txt', 'r')
            lines = file.readlines()
            file.close()
            lines.pop(0)
            global bar_correction
            if lines[0][0] == '0':
                bar_correction = False
            else:
                bar_correction = True
            global rate
            rate = int(lines[0][2:])
            lines.pop(0)
            for line in lines:
                o = threading.Thread(target=load_line, args=(line,))
                o.start()
            while threading.active_count() > 1:
                time.sleep(0.01)
        else:
            messagebox.showinfo(title='Config file created',
                                message='No config file detected!\nCreated configuration file')
            file = open('config.txt', 'w')
            file.write("Configuration file\n0 144\n")
            file.close()
        return is_ok

    ok = file_load()
    while not ok:
        if messagebox.askretrycancel(title="Load error", message="Some lights can't be loaded\nMAKE SURE IS POWERED ON "
                                                                 "AND CONNECTED TO WIFI AND THEN TRY AGAIN\nRetry-try"
                                                                 " again Cancel-Continue with loaded lights"):
            while len(bulbs) > 0:
                bulbs.pop()
            ok = file_load()
        else:
            save_configuration_to_file()
            ok = True


def save_configuration_to_file():
    file = open('config.txt', 'w')
    file.write("Configuration file\n")
    global bar_correction
    if bar_correction is True:
        file.write('1 ')
    else:
        file.write('0 ')
    global rate
    file.write(str(rate))
    file.write('\n')
    for x in bulbs:
        file.write(str(x[0]) + ' ' + x[2] + ' ' + str(x[3]) + '\n')
    file.close()


def modify_configuration():
    def exit_from_config():
        global rate
        rate = int(rate_input.get())
        save_configuration_to_file()
        configuration_window.destroy()
        start_button['state'] = NORMAL
        config_button['state'] = NORMAL
        exit_button['state'] = NORMAL

    def identify():
        try:
            bulbs[bulb_list.curselection()[0]][1].identify()
        except:
            messagebox.showerror(title='ERROR!', message='You need to select a light')

    def black_check_update():
        global bar_correction
        if check.get() == 1:
            bar_correction = True
        else:
            bar_correction = False
        save_configuration_to_file()

    global bulb_list
    global add_bulb_button
    global add_bulb_auto_button
    global identify_button_config
    global edit_bulb_button
    global del_bulb_button
    global exit_button_config
    global start_button
    global config_button
    global exit_button
    global main_window
    global configuration_window
    start_button['state'] = DISABLED
    config_button['state'] = DISABLED
    exit_button['state'] = DISABLED
    configuration_window = Toplevel(main_window)
    configuration_window.resizable(False, False)
    configuration_window.title("Edit Configuration")
    configuration_window.iconbitmap('Logo2.ico')
    bulb_list = Listbox(configuration_window, font=("Arial", 12), width=50, height=10)
    bulb_list.grid(row=0, rowspan=4, column=0, columnspan=2)
    show_bulbs()
    add_bulb_button = Button(configuration_window, text="Add new light manual", command=add_bulb, font=("Arial", 17),
                             width=17)
    global bar_correction
    if bar_correction is True:
        check = IntVar(value=1)
    else:
        check = IntVar()
    black_bar_check = Checkbutton(configuration_window, text="Correct black bars", variable=check,
                                  command=black_check_update, font=("Arial", 17), width=15)
    black_bar_check.grid(row=4, column=0, columnspan=2)
    rate_text = Label(configuration_window, text="Updates per min (max 2500)", font=("Arial", 17))
    rate_text.grid(row=5, column=0)

    def validate(u_input):
        if u_input.isdigit():
            if rate_input.get() == '':
                input_number = int(u_input)
            else:
                input_number = int(rate_input.get()) * 10 + int(u_input)
            if input_number > 2500:
                rate_input.delete(0, END)
                rate_input.after_idle(lambda: rate_input.configure(validate="all"))
                rate_input.insert(0, '')
                return False
            else:
                return True
        else:
            return False

    my_valid = configuration_window.register(validate)
    rate_input = Entry(configuration_window, validate='key', validatecommand=(my_valid, '%S'), font=("Arial", 17),
                       width=10)
    rate_input.grid(row=5, column=1)
    global rate
    rate_input.insert(0, str(rate))
    add_bulb_button.grid(row=1, column=2)
    add_bulb_auto_button = Button(configuration_window, text="Add new light auto", command=add_bulb_auto,
                                  font=("Arial", 17), width=17)
    add_bulb_auto_button.grid(row=0, column=2)
    edit_bulb_button = Button(configuration_window, text="Edit selected light", command=edit_bulb, font=("Arial", 17),
                              width=17)
    edit_bulb_button.grid(row=2, column=2)
    del_bulb_button = Button(configuration_window, text="Delete selected light", command=del_bulb, font=("Arial", 17),
                             width=17)
    del_bulb_button.grid(row=3, column=2)
    exit_button_config = Button(configuration_window, text="Exit", command=exit_from_config, font=("Arial", 17),
                                width=17)
    exit_button_config.grid(row=5, column=2)
    identify_button_config = Button(configuration_window, text="Identify selected", command=identify,
                                    font=("Arial", 17), width=17)
    identify_button_config.grid(row=4, column=2)
    configuration_window.protocol("WM_DELETE_WINDOW", exit_from_config)
    configuration_window.mainloop()


def disable_config_buttons():
    global add_bulb_button
    global add_bulb_auto_button
    global edit_bulb_button
    global del_bulb_button
    global exit_button_config
    global identify_button_config
    add_bulb_button['state'] = DISABLED
    add_bulb_auto_button['state'] = DISABLED
    edit_bulb_button['state'] = DISABLED
    del_bulb_button['state'] = DISABLED
    exit_button_config['state'] = DISABLED
    identify_button_config['state'] = DISABLED


def enable_config_buttons():
    global add_bulb_button
    global add_bulb_auto_button
    global edit_bulb_button
    global del_bulb_button
    global exit_button_config
    global identify_button_config
    add_bulb_button['state'] = NORMAL
    add_bulb_auto_button['state'] = NORMAL
    edit_bulb_button['state'] = NORMAL
    del_bulb_button['state'] = NORMAL
    exit_button_config['state'] = NORMAL
    identify_button_config['state'] = NORMAL


def add_bulb_auto():
    bulb_ips = []

    def auto_discover():
        def try_one_adapter(z):
            try:
                d = discover_bulbs(interface=z)
                for x in d:
                    line = str(x)
                    k1 = line.find('ip') + 6
                    k2 = line.find('port') - 4
                    ip = line[k1:k2]
                    new_bulb = True
                    for b in bulbs:
                        if b[2] == ip:
                            new_bulb = False
                            break
                    if new_bulb:
                        bulb_ips.append(ip)
                        discovered_bulbs_list.insert(discovered_bulbs_list.size(), ip)
            except:
                pass

        adap = ifaddr.get_adapters()
        for j in range(len(adap)):
            k = str(adap[j].nice_name)
            if 'virtual' in k:
                continue
            elif 'Virtual' in k:
                continue
            a = adap[j].name
            o = threading.Thread(target=try_one_adapter, args=(a,))
            o.start()

    def add_bulb_in_list():
        global bulb_list
        try:
            k = int(discovered_bulbs_list.curselection()[0])
            prop = Bulb(bulb_ips[k - 1]).get_capabilities()
            if ' set_hsv ' in prop['support'] or ' bg_set_hsv ' in prop['support']:
                bulbs.append(
                    (position_string_to_int(position_input.get()), BulbYeelight(bulb_ips[k - 1]), bulb_ips[k - 1],
                     int(brightness_slider.get())))
                bulb_ips.pop(k - 1)
                discovered_bulbs_list.delete(k)
                x = len(bulbs) - 1
                pos = position_int_to_string(bulbs[x][0])
                bulb_list.insert(x + 1, pos + ' ' + bulbs[x][2] + " brightness " + str(bulbs[x][3]) + '%')
                save_configuration_to_file()
            else:
                messagebox.showerror(title='ERROR!', message='Light not supported')
        except:
            messagebox.showerror(title='ERROR!', message='You need to select a light in order to add it')

    def identify():
        try:
            k = int(discovered_bulbs_list.curselection()[0])
            BulbYeelight(bulb_ips[k - 1]).identify()
        except:
            messagebox.showerror(title='ERROR!', message='You need to select a light')

    def exit_from_add():
        auto_add_window.destroy()
        enable_config_buttons()

    global configuration_window
    disable_config_buttons()
    auto_add_window = Toplevel(configuration_window)
    auto_add_window.resizable(False, False)
    auto_add_window.title("Auto add lights")
    auto_add_window.iconbitmap('Logo2.ico')
    discovered_bulbs_list = Listbox(auto_add_window, font=("Arial", 12), width=50, height=12)
    discovered_bulbs_list.grid(row=0, rowspan=6, column=0)
    auto_discover()
    position_text = Label(auto_add_window, text="Select light's position", font=("Arial", 17))
    position_text.grid(column=1, row=0, columnspan=2)
    position_input = StringVar(auto_add_window)
    position_input.set("WHOLE SCREEN")
    position_option_menu = OptionMenu(auto_add_window, position_input, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM", "RIGHT",
                                      "TOP-CENTRE", "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE", "CORNER-TOP-LEFT",
                                      "CORNER-BOTTOM-LEFT", "CORNER-BOTTOM-RIGHT", "CORNER-TOP-RIGHT")
    position_option_menu.config(font=("Arial", 15), width=30, height=1)
    position_option_menu.grid(column=1, row=1, columnspan=2)
    brightness_text = Label(auto_add_window, text="Select light's brightness", font=("Arial", 17))
    brightness_text.grid(column=1, row=2, columnspan=2)
    brightness_slider = Scale(auto_add_window, from_=100, to=0, orient=HORIZONTAL, tickinterval=10, resolution=10,
                              font=("Arial", 10), length=350)
    brightness_slider.set(100)
    brightness_slider.grid(column=1, row=3, columnspan=2)
    identity_button = Button(auto_add_window, text="Identify selected", command=identify, font=("Arial", 17), width=27)
    identity_button.grid(column=1, row=4, columnspan=2)
    add_button = Button(auto_add_window, text="Add", command=add_bulb_in_list, font=("Arial", 17), width=13)
    add_button.grid(column=1, row=5)
    exit_add = Button(auto_add_window, text="Exit", command=exit_from_add, font=("Arial", 17), width=13)
    exit_add.grid(column=2, row=5)
    auto_add_window.protocol("WM_DELETE_WINDOW", exit_from_add)
    auto_add_window.mainloop()


def edit_bulb():
    global bulb_list
    global position_change

    def save_edit():
        pos, bulb, ip, bright = bulbs[k]
        pos = position_string_to_int(str(position_change.get()))
        bright = int(brightness_slider.get())
        bulbs[k] = (pos, bulb, ip, bright)
        bulb_list['state'] = NORMAL
        bulb_list.delete(k)
        pos = position_int_to_string(bulbs[k][0])
        bulb_list.insert(k, pos + ' ' + bulbs[k][2] + " brightness " + str(bulbs[k][3]) + '%')
        save_configuration_to_file()
        exit_edit()

    def exit_edit():
        edit_window.destroy()
        bulb_list['state'] = NORMAL
        enable_config_buttons()

    try:
        global configuration_window
        k = int(bulb_list.curselection()[0])
        bulb_list['state'] = DISABLED
        disable_config_buttons()
        edit_window = Toplevel(configuration_window)
        edit_window.resizable(False, False)
        edit_window.title("Edit light's info")
        edit_window.iconbitmap('Logo2.ico')
        position_text = Label(edit_window, text="Select light's position", font=("Arial", 17))
        position_text.pack()
        position_change = StringVar(edit_window)
        position_change.set(position_int_to_string(bulbs[k][0]))
        position_option_menu = OptionMenu(edit_window, position_change, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM",
                                          "RIGHT", "TOP-CENTRE", "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE",
                                          "CORNER-TOP-LEFT", "CORNER-BOTTOM-LEFT", "CORNER-BOTTOM-RIGHT",
                                          "CORNER-TOP-RIGHT")
        position_option_menu.config(font=("Arial", 15), width=30, height=1)
        position_option_menu.pack()
        brightness_text = Label(edit_window, text="Select light's brightness", font=("Arial", 17))
        brightness_text.pack()
        brightness_slider = Scale(edit_window, from_=100, to=0, orient=HORIZONTAL, tickinterval=10, resolution=10,
                                  font=("Arial", 10), length=350)
        brightness_slider.set(bulbs[k][3])
        brightness_slider.pack()
        done_button = Button(edit_window, text="Save current settings", command=save_edit, font=("Arial", 17), width=22)
        done_button.pack()
        exit_button = Button(edit_window, text="Exit", command=exit_edit, font=("Arial", 17), width=22)
        exit_button.pack()
        edit_window.protocol("WM_DELETE_WINDOW", exit_edit)
        edit_window.mainloop()
    except:
        messagebox.showerror(title='ERROR!', message='You need to select a light in order to edit')


def add_bulb():
    def add_bulb_in_list():
        global bulb_list
        ip = str(ip_entry_box.get())
        pos = str(position_input.get())
        pos_txt = pos
        pos = position_string_to_int(pos)
        bright = int(brightness_slider.get())
        error = False
        try:
            prop = Bulb(ip).get_capabilities()
            if ' set_hsv ' in prop['support'] or ' bg_set_hsv ' in prop['support']:
                pass
            else:
                error = True
                messagebox.showerror(title='ERROR!', message='Light not supported')
        except:
            error = True
            messagebox.showerror(title='ERROR!', message='Wrong ip or light is offline')
        if not error:
            bulbs.append((pos, BulbYeelight(ip), ip, bright))
            title = pos_txt + ' ' + ip + " brightness " + str(bright) + '%'
            bulb_list.insert(bulb_list.size(), title)
            file = open('config.txt', 'a')
            file.write(str(pos) + ' ' + ip + ' ' + str(bright) + '\n')
            add_bulb_window.destroy()

    def exit_from_add():
        add_bulb_window.destroy()
        enable_config_buttons()

    global ip_entry_box
    global add_bulb_window
    global configuration_window
    disable_config_buttons()
    add_bulb_window = Toplevel(configuration_window)
    add_bulb_window.resizable(False, False)
    add_bulb_window.title("Add a new light")
    add_bulb_window.iconbitmap('Logo2.ico')
    position_text = Label(add_bulb_window, text="Select light's position", font=("Arial", 17))
    position_text.grid(column=0, row=0)
    position_input = StringVar(add_bulb_window)
    position_input.set("WHOLE SCREEN")
    position_option_menu = OptionMenu(add_bulb_window, position_input, "WHOLE SCREEN", "TOP", "LEFT", "BOTTOM", "RIGHT",
                                      "TOP-CENTRE", "LEFT-CENTRE", "BOTTOM-CENTRE", "RIGHT-CENTRE", "CORNER-TOP-LEFT",
                                      "CORNER-BOTTOM-LEFT", "CORNER-BOTTOM-RIGHT", "CORNER-TOP-RIGHT")
    position_option_menu.config(font=("Arial", 15), width=30, height=1)
    position_option_menu.grid(column=0, row=1)
    info_text = Label(add_bulb_window, text="Enter light's ip", font=("Arial", 17))
    info_text.grid(column=0, row=2)
    ip_entry_box = Entry(add_bulb_window, font=("Arial", 17))
    ip_entry_box.grid(column=0, row=3)
    brightness_text = Label(add_bulb_window, text="Select light's brightness", font=("Arial", 17))
    brightness_text.grid(column=0, row=4)
    brightness_slider = Scale(add_bulb_window, from_=100, to=0, orient=HORIZONTAL, tickinterval=10, resolution=10,
                              font=("Arial", 10), length=350)
    brightness_slider.set(100)
    brightness_slider.grid(column=0, row=5)
    add_button = Button(add_bulb_window, text="Add", command=add_bulb_in_list, font=("Arial", 17), height=4, width=10)
    add_button.grid(column=1, row=0, rowspan=3)
    exit_add = Button(add_bulb_window, text="Exit", command=exit_from_add, font=("Arial", 17), height=4, width=10)
    exit_add.grid(column=1, row=3, rowspan=3)
    add_bulb_window.protocol("WM_DELETE_WINDOW", exit_from_add)
    add_bulb_window.mainloop()


def del_bulb():
    global bulb_list
    try:
        k = int(bulb_list.curselection()[0])
        bulb_list.delete(k)
        bulbs.pop(k)
        save_configuration_to_file()
    except:
        messagebox.showerror(title='ERROR!', message='You need to select a light in order to remove')


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
        while threading.active_count() > 1:
            time.sleep(0.01)
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
    bulbs.sort(key=lambda x: x[0])

    def save_state(i):
        bulbs[i][1].initial_state()

    def revert_state(i):
        bulbs[i][1].revert_to_initial()

    for i in range(len(bulbs)):
        x = threading.Thread(target=save_state, args=(i,))
        x.start()
    while threading.active_count() > 2:
        time.sleep(0.01)
    last_hsv = [[None for _ in range(3)] for _ in range(13)]
    time_after = float(time.time())
    c = 0
    while run:
        c += 1
        c %= 5
        scr = get_screenshot(c)
        i = 0
        while i < len(bulbs):
            k = bulbs[i][0]
            h, s, v = determine_hsv(scr, k)
            if last_hsv[k][0] == h and last_hsv[k][1] == s and last_hsv[k][2] == v:
                while i < len(bulbs) and bulbs[i][0] == k:
                    i += 1
            else:
                last_hsv[k][0] = h
                last_hsv[k][1] = s
                last_hsv[k][2] = v
                while i < len(bulbs) and bulbs[i][0] == k:
                    brightness = bulbs[i][3]
                    v1 = int(v * brightness / 100)
                    bulbs[i][1].set_hsv(h, s, v1, 60 / rate * 1000)
                    i += 1
        time_before = float(time.time())
        time_since_last = time_before - time_after
        if time_since_last < 60 / rate:
            time.sleep(60 / rate - time_since_last)
        time_after = float(time.time())
    for i in range(len(bulbs)):
        x = threading.Thread(target=revert_state, args=(i,))
        x.start()
    while threading.active_count() > 2:
        time.sleep(0.01)


if __name__ == "__main__":
    def close_main_window():
        global run
        run = False
        main_window.destroy()


    global start_button
    global config_button
    global exit_button
    global main_window
    load()
    main_window = Tk()
    main_window.resizable(False, False)
    main_window.title("Yeembilight")
    main_window.iconbitmap('Logo2.ico')
    start_button = Button(main_window, text="Start", command=start, font=("Arial", 20), width=30)
    start_button.grid(row=0, column=0, columnspan=2)
    config_button = Button(main_window, text="Edit configuration", command=modify_configuration, font=("Arial", 20),
                           width=15)
    config_button.grid(row=1, column=0)
    exit_button = Button(main_window, text="Exit", command=main_window.destroy, font=("Arial", 20), width=15)
    exit_button.grid(row=1, column=1)
    main_window.protocol("WM_DELETE_WINDOW", close_main_window)
    main_window.mainloop()
