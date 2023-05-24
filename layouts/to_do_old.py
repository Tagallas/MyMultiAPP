from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox

from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

import sqlite3

from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu

menu_button_ratio = 8
side_menu_button_ratio = 15
m_size_global = Window.size[0] / menu_button_ratio
s_butt_size_global = Window.size[1] / side_menu_button_ratio


class ToDoList(RelativeLayout):
    # s_menu = None
    m_size = m_size_global

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ToDoListHeader())
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name FROM Labels WHERE id_default=1")
        items = db.fetchone()
        database.close()
        self.display_main_screen(items[0])

        # self.menu = SideMenu2()

    def display_main_screen(self, label_name):
        # if self.s_menu:
        #     self.on_menu_exit()
        # top = height-m_size
        self.add_widget(ToDoListScroll(label_name))

    def on_menu_click(self, button):
        # self.s_menu = SideMenu()
        # self.add_widget(self.s_menu)
        self.menu.caller = button
        self.menu.open()

    def on_menu_exit(self):
        # self.remove_widget(self.s_menu)
        pass


class ToDoListMainScreen(BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT rowid FROM Labels WHERE label_name='{}'".format(text))
        label_id = db.fetchone()[0]
        # database.commit()
        db.execute("""SELECT N.deadline, N.priority,  N.note, N.image, N.active
                    FROM Labels LEFT JOIN Notes AS N on Labels.ROWID = N.label_id 
                    WHERE N.label_id = {} AND N.active=0
                    ORDER BY N.active, N.priority, N.deadline
                    """.format(label_id))
        items = db.fetchall()
        for it in items:
            dictionary = {'deadline': it[0], 'priority': it[1], 'note': it[2], 'image': it[3],
                          'is_active': it[4]}
            self.add_widget(CheckNote(dictionary))
        self.add_widget(AddNote())
        database.close()

    def on_checkpoint(self, v):
        print('checkpoint')


class ToDoListScroll(ScrollView):
    size_hint = 1, None
    height = NumericProperty(Window.size[1] - m_size_global * 1.1)

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ToDoListMainScreen(text))


class ToDoListHeader(BoxLayout):
    m_size = m_size_global


# class SideMenu2(MDDropdownMenu):
#     s_butt_size = s_butt_size_global
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.position = "bottom"
#         self.width_mult = 4
#         self.ver_growth = "down"
#         # self.header_cls =
#
#         database = sqlite3.connect('databases/to_do.db')
#         db = database.cursor()
#         db.execute("SELECT rowid, label_name FROM Labels ORDER BY priority, label_name")
#         items = db.fetchall()
#         menu_items = []
#         for it in items:
#             menu_items.append({
#                 "text": it[1],
#                 "viewclass": "OneLineListItem",
#                 "height": self.s_butt_size
#                 #"on_release": lambda x=f"Item {i}": self.menu_callback(x),
#             })
#         self.items = menu_items

# class SideMenu(RelativeLayout):
#     s_butt_size = s_butt_size_global


class SideMenuButtons(StackLayout):
    s_butt_size = s_butt_size_global

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SideMenuHeader())
        self.add_widget(Label(text='To Do', size_hint=(1, None), height=self.s_butt_size))

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT rowid, label_name FROM Labels ORDER BY priority, label_name")
        items = db.fetchall()
        for it in items:
            self.add_widget(MDRaisedButton(text=it[1], font_size=15,
                                           size_hint=(1, None), height=self.s_butt_size,
                                           md_bg_color=(.3, .4, .9, .55), rounded_button=False, _radius=5,
                                            on_release=self.change_label))

        database.commit()
        database.close()

    def change_label(self, button):
        print('zmiana na rowid = '+button.text)


class SideMenuHeader(BoxLayout):
    m_size = m_size_global


class CheckNote(BoxLayout):
    m_size = m_size_global

    def __init__(self, items, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(size_hint=(.05, 1)))
        self.add_widget(CheckBox(active=items['is_active'], size_hint=(.1, 1)))
        self.add_widget(Label(size_hint=(.05, 1)))
        self.add_widget(TextInput(size_hint=(1, 1), text=items['note'], multiline=False,
                                  foreground_color=(1, 1, 1, 1), background_color=(0, 0, 0, 1),
                                  halign='left', font_size=self.height/2.7, padding_y=(self.height/4.05, 0),
                                  cursor_color=(1, 1, 1, 1)))
        # self.add_widget(Button(text=items['note'], size_hint=(.5, 1)))


class AddNote(BoxLayout):
    m_size = m_size_global

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(size_hint=(.2, 1)))
        self.add_widget(Button(background_normal='images/add_sign.png', size_hint=(None, 1), width=self.m_size,
                               on_press=self.add_note, background_down='images/black_screen.png'))
        self.add_widget(Button(text='Add Note', font_size=self.height/2.7, size_hint=(.4, 1),
                               background_color=(0, 0, 0, 1), on_press=self.add_note))
        self.add_widget(Label())

    def add_note(self, button):
        print('note added')
