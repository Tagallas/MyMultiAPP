from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button

import sqlite3

from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout

menu_button_ratio = 8
side_menu_button_ratio = 10
m_size_global = Window.size[0] / menu_button_ratio
s_butt_size_global = Window.size[1] / side_menu_button_ratio


class ToDoList(RelativeLayout):
    s_menu = None
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

    def display_main_screen(self, label_name):
        if self.s_menu:
            self.on_menu_exit()
        # top = height-m_size
        self.add_widget(ToDoListScroll(label_name))

    def on_menu_click(self):
        self.s_menu = SideMenu()
        self.add_widget(self.s_menu)

    def on_menu_exit(self):
        self.remove_widget(self.s_menu)


class ToDoListMainScreen(BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT rowid FROM Labels WHERE label_name='{}'".format(text))
        label_id = db.fetchone()[0]
        db.execute("""SELECT N.deadline, N.note, N.image 
                    FROM Labels LEFT JOIN Notes AS N on Labels.ROWID = N.label_id 
                    WHERE N.label_id = {}
                    ORDER BY N.priority, N.deadline
                    """.format(label_id))
        items = db.fetchall()
        for it in items:
            self.add_widget(Button(text=it[1], size_hint=(1, None), height=m_size_global))
        database.close()


class ToDoListScroll(ScrollView):
    size_hint = 1, None
    height = NumericProperty(Window.size[1] - m_size_global * 1.1)

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ToDoListMainScreen(text))


class ToDoListHeader(BoxLayout):
    m_size = m_size_global


class SideMenu(RelativeLayout):
    s_butt_size = s_butt_size_global


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
            self.add_widget(Button(text=it[1], size_hint=(1, None), height=self.s_butt_size,
                                   on_press=self.change_label))
        database.commit()
        database.close()

    def change_label(self, button):
        print('zmiana na rowid = '+button.text)


class SideMenuHeader(BoxLayout):
    m_size = m_size_global

