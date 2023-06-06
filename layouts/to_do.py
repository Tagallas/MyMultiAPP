from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image

from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from time import sleep
import sqlite3

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget, OneLineRightIconListItem, \
    ILeftBody, ILeftBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawerHeader, \
    MDNavigationDrawerLabel, MDNavigationDrawer, MDNavigationDrawerDivider, MDNavigationDrawerItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.widget import MDWidget

from layouts.notebook import Notebook


menu_button_ratio = 8
side_menu_button_ratio = 15
m_size_global = Window.size[0] / menu_button_ratio
s_butt_size_global = Window.size[1] / side_menu_button_ratio
TAG = 'ERROR'


class ToDoList(MDNavigationLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name FROM Labels WHERE id_default=1")
        self.items = db.fetchone()
        database.close()
        global TAG
        TAG = self.items[0]

    def get_tag(self):
        return self.tag


class MainView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.labels = {}
        self.tasks = []
        self.order_by = 'priority'

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT ROWID, label_name FROM Labels ORDER BY priority")
        labels = db.fetchall()  # lista krotek
        for label in labels:
            self.labels[label[1]] = TaskLabel(label[1])
            self.add_widget(self.labels[label[1]])
            db.execute("""SELECT N.active, N.priority, N.note, N.notification, N.eta, N.deadline
            FROM Labels AS L LEFT JOIN Notes AS N ON L.ROWID = N.label_id
            WHERE N.label_id = {} ORDER BY N.active, N.priority, N.deadline""".format(label[0]))
            items = db.fetchall()
            for i in items:
                self.tasks.append(Task(label[1], i[0], i[1], i[2], i[3], i[4], i[5]))
                # self.add_widget(Button(text=str(i), size_hint_y = None, height = Window.size[1] / 13))
                self.add_widget(self.tasks[-1])
        # self.remove_widget(self.labels[1])
        database.close()

    def update(self, order_by, which_label):
        self.clear_widgets()
        if order_by != self.order_by:
            pass  # tu trzeba sortowanie
        if which_label == 'all':
            for task in self.tasks:
                self.add_widget(task)
        if which_label == 'category':
            idx = 0
            for name in self.labels.keys():
                self.add_widget(self.labels[name])
                while idx < len(self.tasks) and self.tasks[idx].name == name:
                    self.add_widget(self.tasks[idx])
                    idx += 1
        else:
            for task in self.tasks:
                if task.name == which_label:
                    self.add_widget(task)


class TaskLabel(BoxLayout):
    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'
        self.add_widget(Label(text=label, size_hint_x=.6))
        self.add_widget(Label(size_hint_x=.2))
        self.add_widget(MDIconButton(icon='trash-can-outline', icon_size=Window.size[1] / 40,
                                     center=(.5, .5), on_release=self.press))

    def press(self, but):
        print(but.icon)


class Task(BoxLayout):
    def __init__(self, label_name, active, priority, note, notification, eta, deadline, **kwargs):
        super().__init__(**kwargs)
        self.name = label_name
        self.priority = priority
        self.eta = eta
        self.deadline = deadline

        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'
        self.add_widget(CheckBox(size_hint_x=.1, active=active))
        self.add_widget(Label(size_hint_x=.01))
        self.add_widget(Image(source='images/add_sign.png', size_hint_x=.1))
        self.add_widget(Label(text=note))
        if notification:
            icon = 'bell'
        else:
            icon = 'bell-off-outline'
        if eta:
            time = '~'+str(eta)+'min'
        else:
            time = '~'
        font_size = Window.size[1]/15/4
        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                MDIconButton(icon='dots-horizontal', on_release=self.press, icon_size=font_size*1.5, size_hint=(.5, .5)),
                MDIconButton(icon=icon, icon_size=font_size*1.2, size_hint=(.5, .5), on_release=self.press),
                size_hint_y=.5
            ),
            Button(text=time, size_hint_y=.2, font_size=font_size*0.8, halign='right', on_release=self.press,
                   background_color=(0, 0, 0, 0)),
            Button(text=deadline, size_hint_y=.3, font_size=font_size*1.1, halign='right', on_release=self.press,
                   background_color=(0, 0, 0, 0)),
            orientation='vertical', size_hint_x=.3
        ))

    def press(self, but):
        print(but.text)


class CustomNavigationDrawer(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global TAG
        self.add_widget(MDNavigationDrawerHeader(title=TAG, padding=(0, 0, 0, 10)))  # source można dodać
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="bell", on_release=self.print, text='bell'),
                                            text="Notifications", text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineRightIconListItem(IconRightWidget(icon="playlist-edit", on_release=self.print, text='edit',),
                                            text="Labels", on_release=self.press, divider=None))

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name FROM Labels ORDER BY priority")
        items = db.fetchall()
        database.close()
        for el in items:
            self.add_widget(OneLineIconListItem(IconLeftWidget(icon="label-outline", on_release=self.print, text='label'),
                                            text=el[0], text_color=(.7, .7, .7, .5),
                                            on_release=self.press, divider=None))

        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="plus", on_release=self.print, text='add'),
                                            text='Add Label', text_color=(.5, .5, .5, .5),
                                            on_release=self.print, divider=None))
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="cog", on_release=self.print, text='cog'),
                                            text='Settings', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="trash-can-outline", on_release=self.print, text='trash-can'),
                                            text='Trash', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="help-circle-outline", on_release=self.print, text='help'),
                                            text='Help', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))

    def print(self, butt):
        print(butt.text)

    def press(self, butt):
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        if butt.text == 'Labels':
            self.parent.parent.parent.ids.main_screen.update('category', 'category')
        else:
            self.parent.parent.parent.ids.main_screen.update('priority', butt.text)

