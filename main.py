from kivy import Config
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '700')

from kivy.properties import BooleanProperty
from kivymd.uix.screen import MDScreen

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.button import Button
# from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import Screen, FadeTransition

# import kivymd.app as app
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager, ScreenManager
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton, BaseButton, MDRaisedButton

# todo zastanów sie które transition
from kivymd.uix.transition import MDFadeSlideTransition

from layouts.to_do import ToDoList
from layouts.notebook import Notebook
from layouts.gym import Gym
from include.db_create import create_all_db

Builder.load_file("kv_screens/to_do.kv")
Builder.load_file("kv_screens/notebook.kv")
Builder.load_file("kv_screens/gym.kv")
Builder.load_file("kv_screens/Multi.kv")

APP = 0
window_width, window_height = Window.size


class MainLayout(StackLayout):
    # menu_buttons = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        butt_size = (.5, .2)
        self.padding = window_width * .07
        self.spacing = window_width * .05
        self.add_widget(MDRaisedButton(text="TO_DO", font_size=23,
                                        size_hint=butt_size, md_bg_color=(.1, .2, .6, .85),
                                        rounded_button=False, _radius=25,
                                        on_release=self.on_press))
        self.add_widget(MDRaisedButton(text="Notebook", font_size=23,
                                        size_hint=butt_size, md_bg_color=(.1, .2, .6, .85),
                                        rounded_button=False, _radius=25,
                                        on_release=self.on_press))
        self.add_widget(MDRaisedButton(text="GYM", font_size=23,
                                        size_hint=butt_size, md_bg_color=(.1, .2, .6, .85),
                                        rounded_button=False, _radius=25,
                                        on_release=self.on_press))

    def on_press(self, button):
        self.parent.parent.on_press_menu(button.text)


class SM(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = FadeTransition()
        #self.screens = [S1(), S2(), S3(), S4()]
        #self.current = 'TO_DO'
        #self.current = 's1'
        #print(self.screen_names)

    def on_press_menu(self, screen_name='s1'):
        self.current = screen_name
        # print(self.screens)


class S1(MDScreen):
    pass


class S2(MDScreen):
    pass


class S3(MDScreen):
    pass


class S4(MDScreen):
    pass


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Indigo'
        self.theme_cls.primary_hue = '900'
        #primary hue
        return Builder.load_file('My.kv')


if __name__ == '__main__':
    MyApp().run()
    #create_all_db()
