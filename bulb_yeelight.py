from yeelight import Bulb
import time


class BulbYeelight:

    def __init__(self, ip):
        self.initial_power = None
        self.initial_brightness = None
        self.initial_color_temp = None
        self.initial_r_value = None
        self.initial_g_value = None
        self.initial_b_value = None
        self.initial_color_mode = None
        self.bulb = []
        self.bulbs = 3
        self.rate = 60 / 144
        self.transition_time = (60 / 144) * 1000
        self.i = 0
        self.time_after = None
        self.time_before = None
        self.nume = ip
        self.time_after = float(time.time())
        for x in range(self.bulbs + 1):
            self.time_before = float(time.time())
            self.bulb.append(Bulb(ip))
            self.after_interact()
            # transition time
            # self.time_before = float(time.time())
            # self.bulb[x].duration = self.transition_time
            # self.after_interact()

    def after_interact(self):
        self.i += 1
        self.i %= self.bulbs
        time_since_last = self.time_before - self.time_after
        if time_since_last < self.rate:
            time.sleep(self.rate - time_since_last)
        self.time_after = float(time.time())

    def initial_state(self):
        self.time_before = float(time.time())
        prop = str(self.bulb[self.i].get_properties())
        self.after_interact()
        if prop[prop.find("'power'") + 11] == 'n':
            self.initial_power = True
        else:
            self.initial_power = False
            self.turn_on()
        k = prop.find("'bright'") + 11
        if prop[k + 2].isdigit():
            self.initial_brightness = 100
        elif prop[k + 1].isdigit():
            self.initial_brightness = int(prop[k]) * 10 + int(prop[k + 1])
        else:
            self.initial_brightness = int(prop[k])
        k = prop.find("'ct'") + 7
        self.initial_color_temp = int(prop[k]) * 1000 + int(prop[k + 1]) * 100 + int(prop[k + 2]) * 10 + int(
            prop[k + 3])
        k = prop.find("'rgb'") + 8
        self.initial_b_value = 0
        while prop[k].isdigit():
            self.initial_b_value = self.initial_b_value * 10 + int(prop[k])
            k += 1
        self.initial_r_value = int(self.initial_b_value / 65536)
        self.initial_b_value = self.initial_b_value % 65536
        self.initial_g_value = int(self.initial_b_value / 256)
        self.initial_b_value = self.initial_b_value % 256
        k = prop.find("'color_mode'")
        if prop[k + 15] == '2':
            self.initial_color_mode = False
        else:
            self.initial_color_mode = True

    def set_color(self, r, g, b):
        self.time_before = float(time.time())
        self.bulb[self.i].set_rgb(r, g, b)
        self.after_interact()

    def set_hsv(self, h, s, v):
        try:
            self.bulb[self.i].set_hsv(h, s, v)
        except Exception:
            pass
        self.i += 1
        self.i %= self.bulbs

    def identify(self):
        print(self.nume)
        self.initial_state()
        self.set_color(255, 0, 0)
        self.set_color(0, 255, 0)
        self.set_color(0, 0, 255)
        self.revert_to_initial()

    def turn_on(self):
        self.time_before = float(time.time())
        self.bulb[self.i].turn_on()
        self.after_interact()

    def revert_to_initial(self):
        if self.initial_color_mode:
            self.time_before = float(time.time())
            self.bulb[self.i].set_brightness(self.initial_brightness)
            self.after_interact()
            self.time_before = float(time.time())
            self.bulb[self.i].set_rgb(self.initial_r_value, self.initial_g_value, self.initial_b_value)
            self.after_interact()
        else:
            self.time_before = float(time.time())
            self.bulb[self.i].set_brightness(self.initial_brightness)
            self.after_interact()
            self.time_before = float(time.time())
            self.bulb[self.i].set_color_temp(self.initial_color_temp)
            self.after_interact()
        if not self.initial_power:
            self.time_before = float(time.time())
            self.bulb[self.i].turn_off()
            self.after_interact()
