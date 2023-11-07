from kivy import Config
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '700')
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import FadeTransition

from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.button import MDRaisedButton

from layouts.to_do import ToDoList
from layouts.notebook import Notebook
from layouts.gym import Gym
from include.db_create import create_all_db

Builder.load_file("kv_screens/to_do.kv")
Builder.load_file("kv_screens/notebook.kv")
Builder.load_file("kv_screens/gym.kv")
Builder.load_file("kv_screens/multi.kv")

window_width, window_height = Window.size


# MENU
class MainLayout(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # size hint of buttons in menu
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

    # print button text when button is not defined yet
    def on_press(self, button):
        self.parent.parent.on_press_menu(button.text)


class SM(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = FadeTransition()

    # changing current screen
    def on_press_menu(self, screen_name='s1'):
        self.current = screen_name


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Indigo'
        self.theme_cls.primary_hue = '900'
        return Builder.load_file('my.kv')


if __name__ == '__main__':
    MyApp().run()
    # creating all empty databases
    # create_all_db()
