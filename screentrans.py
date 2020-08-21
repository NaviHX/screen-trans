# coding=utf-8
import pytesseract
import pynput
from googletrans import Translator
import PIL
import pyscreenshot
from tkinter import *
from functools import partial
import threading

Trans = Translator(service_urls='translate.google.cn')

flag = False
state = 0
start_x = 0
start_y = 0
dest_x = 0
dest_y = 0
language = 'eng'
support_lang = ['eng', 'jpn']
change_func = []


def change_lang(label, lang):
    global language
    global lang_var
    language = lang
    label['text'] = '当前语言: {}'.format(lang)


class GUI:
    def __init__(self):
        self.window = Tk()

    def set_window(self):
        self.window.title('Screen_Trans By NaviHX')
        self.window.geometry('400x200+10+10')
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.5)

        self.list_label = Label(self.window, text='支持的语言列表')
        self.list_label.grid(row=0, column=0)

        self.button_list = []

        self.now_lang = Label(self.window,
                              text='当前语言: {}'.format(support_lang[0]))
        self.now_lang.grid(row=3, column=0)

        for idx in range(len(support_lang)):
            lang = support_lang[idx]
            f = partial(change_lang, label=self.now_lang, lang=lang)
            change_func.append(f)
            b = Button(self.window,
                       text=lang,
                       bg='lightblue',
                       width=10,
                       command=change_func[idx])
            self.button_list.append(b)
            b.grid(row=idx + 1, column=0)

        self.trans = Text(self.window, height=10, width=40)
        self.trans.grid(row=0, column=1, rowspan=10)
        self.trans.insert(1.0, '翻译文本')

    def set_trans(self, s):
        self.trans.delete(1.0, END)
        print('已删除')
        self.trans.insert(1.0, s)
        print('已添加')


gui = GUI()
gui.set_window()


def coordinate_swap(sx, sy, dx, dy):
    x1 = min(sx, dx)
    y1 = min(sy, dy)
    x2 = max(sx, dx)
    y2 = max(sy, dy)
    return x1, y1, x2, y2


def img_trans(img, langs):
    try:
        ret=''
        text = pytesseract.image_to_string(img)
        split_text = text.replace("\n", " ").split(".")
        for i in split_text:
            if i != "":
                i += "."
                translator = Translator()
                translation = translator.translate(i, dest="zh-CN")
                ret+=translation
        return ret
    except Exception as e:
        print(e)
        return ''


def get_img(sx, sy, dx, dy):
    img = pyscreenshot.grab(bbox=(sx, sy, dx, dy))
    return img


def on_click(x, y, button, pressed):
    global state
    global start_x
    global start_y
    global dest_x
    global dest_y
    global flag
    global pad
    if pressed and flag:
        if state == 0:
            start_x = x
            start_y = y
            state += 1
        elif state == 1:
            dest_x = x
            dest_y = y
            start_x, start_y, dest_x, dest_y = coordinate_swap(
                start_x, start_y, dest_x, dest_y)
            s = img_trans(get_img(start_x, start_y, dest_x, dest_y),
                          langs=language)
            gui.set_trans(s)
            state = 0


def on_press(key):
    global flag
    try:
        if key.char == 's':
            print('开始记录坐标')
            flag = True
        elif key.char == 'q':
            print('结束记录坐标')
            flag = False
    except:
        1 + 1


def keyboard_listen():
    with pynput.keyboard.Listener(on_press=on_press) as keyboard_listener:
        keyboard_listener.join()


def mouse_listen():
    with pynput.mouse.Listener(on_click=on_click) as mouse_listener:
        mouse_listener.join()


keyboard_thread = threading.Thread(target=keyboard_listen)
mouse_thread = threading.Thread(target=mouse_listen)

keyboard_thread.start()
mouse_thread.start()

gui.window.mainloop()

print('感谢使用')
