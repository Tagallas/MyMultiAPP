# under development
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

import cv2
import numpy as np
from datetime import date
import sqlite3

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.relativelayout import MDRelativeLayout

import include.variables as global_variables


class CalendarView(MDRelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build_daily(self, date=date.today().strftime('20%y-%m-%d')):
        # self.top_bar = CalendarBar(size_hint_y=None, height=self.parent.parent.children[-1].height/2,
        #                            pos_hint={'top': 1})
        # self.add_widget(self.top_bar)
        self.clear_widgets()
        self.tasks = []

        self.widget_height = Window.size[1]*.07
        self.height = self.widget_height * 25
        self.hours_widgets = []
        for i in range(25):
            self.hours_widgets.append(MDBoxLayout(
                Label(text=str(i)+':00', size_hint_x=.1, font_size=Window.size[1]*.02),
                Label(size_hint_x=.9),
                #Button(size_hint_x=.9, text=str(i)),
                size_hint_y=.1, orientation='horizontal', y=(23-i)*self.widget_height))
            self.add_widget(self.hours_widgets[-1])

        date = '0000-00-00'

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute(f"""SELECT ROWID, priority, note, image, shape, notification_time, eta, calendar FROM Notes
                    WHERE active=0 AND notification='{date}' AND calendar IN (1, 2)  ORDER BY priority """)
        items = db.fetchall()
        for item in items:
            note = item[2]
            if item[3]:
                shape = np.frombuffer(item[4], dtype='int32')
                note = np.frombuffer(item[3], dtype=np.uint8)
                note.shape = shape
            eta = item[6]
            if item[6] == '-':
                eta = 60
            eta = int(eta)/60

            y = self.widget_height*(24-eta-int(item[5][:-3])) - self.widget_height*(int(item[5][-2:])/60)
            p = self.widget_height * .1

            task = CalendarTask(item[0], item[1], note, None, item[7], y=y, height=self.widget_height*eta, padding=(p, p, p, p))
            self.tasks.append(task)
            self.add_widget(task)

        database.close()

    def left_arrow(self):
        print('left')

    def right_arrow(self):
        print('right')

    def reload_task(self, rowid):
        for id, task in enumerate(self.tasks):
            if task.rowid == rowid:
                database = sqlite3.connect('databases/to_do.db')
                db = database.cursor()
                db.execute(f"""SELECT ROWID, priority, note, image, shape, notification_time, eta, calendar FROM Notes
                            WHERE ROWID = {rowid} """)
                item = db.fetchone()
                note = item[2]
                if item[3]:
                    shape = np.frombuffer(item[4], dtype='int32')
                    note = np.frombuffer(item[3], dtype=np.uint8)
                    note.shape = shape
                eta = item[6]
                if item[6] == '-':
                    eta = 60
                eta = int(eta) / 60

                y = self.widget_height * (24 - eta - int(item[5][:-3])) - self.widget_height * (
                            int(item[5][-2:]) / 60)
                p = self.widget_height * .1

                self.remove_widget(self.tasks[id])
                self.tasks[id] = CalendarTask(item[0], item[1], note, None, item[7], y=y, height=self.widget_height * eta,
                                        padding=(p, p, p, p))
                self.add_widget(self.tasks[id])
                database.close()

    def edit(self, but):
        self.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        global_variables.which_label_global = 'calendar'
        global_variables.order_by_global = 'calendar'
        for task in self.parent.parent.parent.parent.ids.main_screen.tasks:
            if task.rowid == int(but.text):
                self.parent.parent.parent.parent.ids.edit_screen.edit_task(task)
                break


class CalendarTask(MDBoxLayout):
    def __init__(self, rowid, priority, note, notification, calendar, **kwargs):
        super().__init__(**kwargs)
        self.rowid = rowid
        self.size_hint = (.9, None)
        self.x = Window.size[0]*.11
        self.y += Window.size[1]*.015
        self.orientation = 'horizontal'
        self.md_bg_color = (global_variables.priority_colors[priority - 1][0] * .3,
                            global_variables.priority_colors[priority - 1][1] * .3,
                            global_variables.priority_colors[priority - 1][2] * .3, 1)

        if isinstance(note, str):
            self.add_widget(Label(text=note, size_hint_x=.8))
        else:
            buf1 = cv2.flip(note, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(note.shape[1], note.shape[0]), colorfmt='luminance')
            image_texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')
            self.add_widget(Image(texture=image_texture, pos_hint={'center_x': .5, 'center_y': .5}, size_hint_x=.8))

        icon = 'bell'
        if calendar == 1:
            icon = 'bell-off-outline'
        self.add_widget(MDIconButton(icon=icon, text=str(rowid), on_release=lambda x=rowid: self.parent.edit(x),
                                     pos_hint={'center_x': .5, 'center_y': .5}, size_hint_x=.8))