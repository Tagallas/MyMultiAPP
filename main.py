from kivy import Config

Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '700')
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, FallOutTransition
from layouts.to_do import ToDoList
from layouts.notebook import Notebook
from layouts.gym import Gym
from include.db_create import create_all_db

Builder.load_file("kv_screens/to_do.kv")
Builder.load_file("kv_screens/notebook.kv")
Builder.load_file("kv_screens/gym.kv")
Builder.load_file("kv_screens/Multi.kv")

# Clock.max_iteration = 100
APP = 0


class MainLayout(StackLayout):
    menu_buttons = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        butt_size = (.5, .2)
        self.padding = (dp(25), dp(25), dp(25), dp(25))
        self.spacing = dp(10)
        self.menu_buttons.append(Button(text="TO_DO", size_hint=butt_size, background_color=(.2, .2, 1, .85),
                                        font_size=23, on_press=self.on_press))
        self.menu_buttons.append(Button(text="Notebook", size_hint=butt_size, background_color=(.2, .2, 1, .85),
                                        font_size=23, on_press=self.on_press))
        self.menu_buttons.append(Button(text="GYM", size_hint=butt_size, background_color=(.2, .2, 1, .85),
                                        font_size=23, on_press=self.on_press))
        for i in self.menu_buttons:
            self.add_widget(i)

    def on_press(self, button):
        self.parent.parent.on_press_menu(button.text) # można options dać

    # def on_press_to_do(self, button):
    #     self.parent.parent.on_press_menu('s2') # można options dać
    #     # if self.parent.main_menu.opacity == 1:
    #     #     # print('todo')
    #     #     global APP
    #     #     APP = ToDoList()
    #     #     self.parent.main_menu.opacity = 0
    #     #     self.parent.update_layout()
    #
    # def on_press_notebook(self, button):
    #     self.parent.parent.on_press_menu('s3') # można options dać
    #     # if self.parent.main_menu.opacity == 1:
    #     #     # print('notebook')
    #     #     global APP
    #     #     APP = Notebook()
    #     #     self.parent.main_menu.opacity = 0
    #     #     self.parent.update_layout()
    #
    # def on_press_gym(self, button):
    #     self.parent.parent.on_press_menu('s4') # można options dać
    #     # if self.parent.main_menu.opacity == 1:
    #     #     # print('gym')
    #     #     global APP
    #     #     APP = Gym()
    #     #     self.parent.main_menu.opacity = 0
    #     #     self.parent.update_layout()


class SM(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screens = [S1(), S2(), S3(), S4()]
        self.current = 'TO_DO'
        #self.current = 's1'
        # print(self.screens)

    def on_press_menu(self, screen_name='s1'):
        self.current = screen_name
        # print(self.screens)


class S1(Screen):
    pass


class S2(Screen):
    pass


class S3(Screen):
    pass


class S4(Screen):
    pass


# class Menu(RelativeLayout):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.main_menu = MainLayout()
#         self.add_widget(self.main_menu)
#
#     def update_layout(self):
#         global APP
#         secondary_menu = APP
#         self.add_widget(secondary_menu)
#
#     def on_press_menu(self):
#         # print('menu')
#         self.main_menu.opacity = 1
#         self.remove_widget(APP)


class MyApp(App):
    pass


if __name__ == '__main__':
    MyApp().run()
    #create_all_db()
