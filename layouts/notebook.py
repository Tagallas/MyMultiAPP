from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRectangleFlatIconButton


class Notebook(BoxLayout):
    num = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.but = MDRectangleFlatIconButton(on_release=self.press, size_hint=(None, None), size=(100, 100))
        self.add_widget(self.but)

    def press(self, but):
        self.but.size = (1, 1)
        x = 1
        for i in range(1, 1000):
            x *= i
        self.but.size = (100, 100)
