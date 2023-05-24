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
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget, OneLineRightIconListItem, \
    ILeftBody, ILeftBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawerHeader, \
    MDNavigationDrawerLabel, MDNavigationDrawer, MDNavigationDrawerDivider, MDNavigationDrawerItem

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
        #self.add_widget(MDNavigationDrawerLabel(text="Labels"))
        self.add_widget(OneLineRightIconListItem(IconRightWidget(icon="playlist-edit", on_release=self.print, text='edit',),
                                            text="Labels", on_release=self.print, divider=None))

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name FROM Labels WHERE id_default=0")
        items = db.fetchall()
        database.close()
        for el in items:
            self.add_widget(OneLineIconListItem(IconLeftWidget(icon="label-outline", on_release=self.print, text='label'),
                                            text=el[0], text_color=(.7, .7, .7, .5),
                                               on_release=self.print, divider=None))
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
