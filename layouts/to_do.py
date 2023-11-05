import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
# from kivy.uix.screenmanager import Screen, NoTransition, FadeTransition, ScreenManager
from kivy.clock import Clock
# from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Line
# from kivy.uix.scrollview import ScrollView
# from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from kivy.graphics.context_instructions import PushMatrix, Rotate, PopMatrix

import cv2
# import matplotlib.pyplot as plt
import numpy as np
from datetime import date
from datetime import datetime
import sqlite3
# import time

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDIcon
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget, OneLineRightIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerHeader, MDNavigationDrawerDivider
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
# from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import Snackbar
# from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
# from kivymd.uix.toolbar import MDTopAppBar

from layouts.notebook import Notebook
import include.get_from_db as get_from_db
from include.sort import sort_task

task_colors = [(1, 0, 0, .9), (245 / 255, 118 / 255, 39 / 255, 0.8), (245 / 255, 217 / 255, 39 / 255, 0.8),
                   (47 / 255, 151 / 255, 33 / 255, 0.8)]

menu_button_ratio = 8
side_menu_button_ratio = 15
m_size_global = Window.size[0] / menu_button_ratio
s_butt_size_global = Window.size[1] / side_menu_button_ratio
TAG = 'TO DO'

order_by_global = 'category'
which_label_global = 'category'
asc_global = 'asc'


class ToDoList(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global TAG
        self.items = TAG
        self.item_height = Window.size[1] / 30

    def get_tag(self):
        return self.tag

    def sort(self):
        self.sort_menu = MDDropdownMenu(caller=self.ids.app_bar,
                       items=self.create_sort_items(), width_mult=2.3, max_height=self.item_height*5+80)
        self.sort_menu.open()

    def delete_trash_dialog(self):
        self.info_window = MDDialog(
            text="Remove trash?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x: self.info_window.dismiss()
                ),
                MDFlatButton(
                    text="REMOVE",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    on_release=self.delete_trash
                ), ], )
        self.info_window.open()

    def delete_trash(self, *args):
        self.info_window.dismiss()
        self.ids.trash_can_view.clear_widgets()
        self.info_window = None
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("""DELETE FROM Trash
             """)
        database.commit()
        database.close()

    def create_sort_items(self):
        return [{
                "viewclass": "MDRectangleFlatIconButton",
                "icon": 'sort',
                "text": "category",
                "halign": "left",
                "icon_size": self.item_height,
                "text_color": (1, 1, 1, 1),
                "icon_color": (1, 1, 1, 1),
                "line_color": (1, 1, 1, 0),
                "theme_text_color": 'Custom',
                "on_release": lambda x='category': {self.ids.main_screen.update(x, x), self.sort_menu.dismiss()}
            },
            {
                "viewclass": "MDRectangleFlatIconButton",
                "icon": 'sort-numeric-ascending',
                "text": "priority",
                "halign": "left",
                "icon_size": self.item_height,
                "text_color": (1, 1, 1, 1),
                "icon_color": (1, 1, 1, 1),
                "line_color": (1, 1, 1, 0),
                "theme_text_color": 'Custom',
                "on_release": lambda x=('priority', None, 'asc'): {self.ids.main_screen.update(x[0], x[1], x[2]),
                                                                    self.sort_menu.dismiss()}
            },
            {
                "viewclass": "MDRectangleFlatIconButton",
                "icon": 'sort-numeric-descending',
                "text": "priority desc",
                "halign": "left",
                "icon_size": self.item_height,
                "text_color": (1, 1, 1, 1),
                "icon_color": (1, 1, 1, 1),
                "line_color": (1, 1, 1, 0),
                "theme_text_color": 'Custom',
                "on_release": lambda x=('priority', None, 'desc'): {self.ids.main_screen.update(x[0], x[1], x[2]),
                                                                    self.sort_menu.dismiss()}
            },
            {
                "viewclass": "MDRectangleFlatIconButton",
                "icon": 'sort-clock-ascending-outline',
                "text": "deadline",
                "halign": "left",
                "icon_size": self.item_height,
                "text_color": (1, 1, 1, 1),
                "icon_color": (1, 1, 1, 1),
                "line_color": (1, 1, 1, 0),
                "theme_text_color": 'Custom',
                "on_release": lambda x=('deadline', None, 'asc'): {self.ids.main_screen.update(x[0], x[1], x[2]),
                                                                    self.sort_menu.dismiss()}
            },
            {
                "viewclass": "MDRectangleFlatIconButton",
                "icon": 'sort-clock-descending-outline',
                "text": "deadline desc",
                "halign": "left",
                "icon_size": self.item_height,
                "text_color": (1, 1, 1, 1),
                "icon_color": (1, 1, 1, 1),
                "line_color": (1, 1, 1, 0),
                "theme_text_color": 'Custom',
                "on_release": lambda x=('deadline', None, 'desc'): {self.ids.main_screen.update(x[0], x[1], x[2]),
                                                                    self.sort_menu.dismiss()}
            },
        ]


class NavigationDrawerScreenManager(MDScreenManager): #  TODO tu musi być screenmanager żeby nie było laga
    pass


class MainView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.labels = {rowid: LabelLayout(), }
        self.labels = {}
        self.tasks = []

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT ROWID, label_name, priority FROM Labels ORDER BY priority")
        labels = db.fetchall()
        for label in labels:
            # t_start = time.perf_counter()
            self.labels[label[0]] = LabelLayout(label[0], label[1], label[2])
            self.add_widget(self.labels[label[0]])
            db.execute("""SELECT N.active, N.priority, N.note, N.notification, N.eta, N.deadline, N.notification_time,
                        N.ROWID, N.image, N.shape
            FROM Labels AS L LEFT JOIN Notes AS N ON L.ROWID = N.label_id
            WHERE N.label_id = {} ORDER BY N.active, N.priority, N.deadline""".format(label[0]))
            items = db.fetchall()
            # t_stop = time.perf_counter()
            # print("Czas obliczeń:", "{:.7f}".format(t_stop - t_start))

            for i in items:
                if i[9] is None:
                    self.tasks.append(Task(label[1], str(label[0]), i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
                else:
                    # continue
                    shape = np.frombuffer(i[9], dtype='int32')  # shape -> array[height, width]
                    img = np.frombuffer(i[8], dtype=np.uint8)  # img -> array[n, 1]
                    img.shape = shape
                    self.tasks.append(Task(label[1], str(label[0]), i[0], i[1], img, i[3], i[4], i[5], i[6], i[7]))
                self.labels[label[0]].add_task(self.tasks[-1])

        database.close()

    def add_task(self, task):
        self.tasks.append(task)

    def reload_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                prev_id = int(self.tasks[i].label_id)
                database = sqlite3.connect('databases/to_do.db')
                db = database.cursor()
                db.execute(f"""SELECT active, priority, note, notification, eta, deadline, notification_time,
                        ROWID, label_id, image, shape FROM Notes WHERE ROWID = {rowid}""")
                it = db.fetchone()

                db.execute(f"""SELECT label_name FROM Labels WHERE ROWID = {it[8]}""")
                lt = db.fetchone()

                if it[10] is None:
                    self.tasks[i] = Task(lt[0], it[8], it[0], it[1], it[2], it[3], it[4], it[5], it[6], it[7])
                else:
                    shape = np.frombuffer(it[10], dtype='int32')
                    img = np.frombuffer(it[9], dtype=np.uint8)
                    img.shape = shape
                    self.tasks[i] = Task(lt[0], it[8], it[0], it[1], img, it[3], it[4], it[5], it[6], it[7])

                if int(prev_id) != it[8]:
                    self.labels[prev_id].remove_task(rowid)
                    self.labels[it[8]].add_task(self.tasks[i])
                else:  # gdy nie ma zmiany label_name
                    self.labels[it[8]].remove_task(rowid)
                    self.labels[it[8]].add_task(self.tasks[i])

                global which_label_global
                if which_label_global not in ('all', 'calendar'):
                    self.labels[it[8]].sort_label_layout()

                database.close()
                return

    def disable_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                task = self.tasks[i]
                task.opacity = .3
                self.remove_widget(task)
                self.add_widget(task)
                return

    def activate_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                task = self.tasks[i]
                task.opacity = 1
                self.update()
                return

    # zmienia label_name / dodaje nową label_name
    def reload_labels(self, rowid, label_name, priority=None):
        if rowid in self.labels.keys():
            self.labels[rowid].reload_label()
            self.update(None, int(rowid))
        else:  # tutaj dodajesz label
            global which_label_global, order_by_global
            self.labels[rowid] = LabelLayout(rowid, label_name, priority)
            self.update('priority', int(rowid), 'asc')

    def remove_label(self, rowid):
        for task in self.tasks:
            if task.label_id == rowid:
                self.tasks.remove(task)
        self.remove_widget(self.labels[rowid])
        del self.labels[rowid]

    def update(self, order_by=None, which_label=None, asc=None):
        global order_by_global, which_label_global, asc_global
        self.clear_widgets()
        if order_by is None:
            order_by = order_by_global
        if which_label is None:
            which_label = which_label_global
        if asc is None:
            asc = asc_global

        order_by_global = order_by
        asc_global = asc
        which_label_global = which_label

        if order_by == 'category':
            database = sqlite3.connect('databases/to_do.db')
            db = database.cursor()
            db.execute("SELECT ROWID FROM Labels ORDER BY priority")
            ids = db.fetchall()
            for i in ids:
                self.labels[i[0]].sort_label_layout('category', 'asc')
                self.add_widget(self.labels[i[0]])

            database.close()

        else:
            if which_label == 'category':
                which_label = 'all'
                which_label_global = which_label

            if which_label == 'all':
                for key in self.labels.keys():
                    self.labels[key].hide_tasks()

                sort_task(self.tasks)
                if asc == 'desc':
                    length = len(self.tasks)
                    for i in range(int(length/2)):
                        self.tasks[i], self.tasks[length-i-1] = self.tasks[length-i-1], self.tasks[i]

                disabled = []
                for task in self.tasks:
                    if not task.active:
                        self.add_widget(task)
                    else:
                        disabled.append(task)

                for task in disabled:
                    self.add_widget(task)

            else:
                self.labels[which_label].sort_label_layout(order_by, asc)
                self.add_widget(self.labels[which_label])


class LabelLayout(MDBoxLayout):
    def __init__(self, rowid, label_name, priority, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None

        self.priority = priority
        self.rowid = rowid
        self.widget_height = Window.size[1] / 13
        self.height = self.widget_height * 1.65

        self.tasks = []
        self.disabled_tasks = []
        self.label = TaskLabel(label_name)
        self.add_widget(self.label)
        self.add_widget(MDBoxLayout(
            Label(size_hint_x=.1),
            MDRectangleFlatIconButton(icon='plus', text='Add Task', on_release=lambda x: self.add_window(),
                size_hint=(.7, None), text_color=(1, 1, 1, 1), line_color=(1, 1, 1, 0),
                icon_color=(1, 1, 1, 1), md_bg_color=(.1, .1, .1, .03)),
            MDIconButton(icon='camera-plus-outline', on_release=lambda x: self.add_photo(self.rowid, label_name),
                size_hint=(.2, None), text_color=(1, 1, 1, 1), line_color=(1, 1, 1, 0),
                icon_color=(1, 1, 1, 1), md_bg_color=(.1, .1, .1, .03), pos_hint={'center_y': .53}),
            orientation='horizontal'))

    def hide_tasks(self):
        for task in self.tasks:
            self.remove_widget(task)
        for d_task in self.disabled_tasks:
            self.remove_widget(d_task)

    def disable_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                task = self.tasks[i]
                size = len(self.tasks) + len(self.disabled_tasks)
                del self.tasks[i]
                self.disabled_tasks.append(task)
                task.opacity = .3
                for j in range(i, len(self.tasks)):
                    self.children[size-j-1], self.children[size-j] = self.children[size-j], self.children[size-j-1]
                return

    def activate_task(self, rowid):
        for i in range(len(self.disabled_tasks)):
            if self.disabled_tasks[i].rowid == rowid:
                task = self.disabled_tasks[i]
                del self.disabled_tasks[i]
                self.tasks.append(task)
                task.opacity = 1
                self.sort_label_layout()
                return

    def add_window(self):
        self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        self.parent.parent.parent.parent.parent.ids.edit_screen.add_task(self.rowid, self.label.label_name)

    def remove_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                global which_label_global
                if which_label_global != 'all':
                    self.remove_widget(self.tasks[i])
                self.height -= self.widget_height

                del self.tasks[i]
                return

    def remove_disabled(self):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        for task in self.disabled_tasks:
            self.height -= self.widget_height
            self.remove_widget(task)

            note = ''
            img = None
            shape = None
            if isinstance(task.note, str):
                note = task.note
            else:
                img = sqlite3.Binary(task.note)
                shape = np.array(task.note.shape)

            db.execute("""
                    INSERT INTO Trash (label_id, priority, deadline, note, image, eta, notification, 
                    notification_time, deleted_date, shape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (task.label_id, task.priority, task.deadline, note, img, task.eta, task.notification,
                          task.notification_time, str(date.today().strftime("20%y-%m-%d")), shape))

            database.commit()
            db.execute(f"""
                            DELETE FROM Notes
                            WHERE ROWID = {task.rowid};
                        """)
            database.commit()
        self.disabled_tasks = []
        database.close()

    def sort_label_layout(self, order_by=None, asc=None):
        global order_by_global, asc_global, which_label_global
        if order_by is not None:
            order_by_global = order_by
        if asc is not None:
            asc_global = asc
        sort_task(self.tasks)

        if asc == 'desc':
            length = len(self.tasks)
            for i in range(int(length / 2)):
                self.tasks[i], self.tasks[length - i - 1] = self.tasks[length - i - 1], self.tasks[i]

        for task in self.tasks:
            self.remove_widget(task)
        for task in self.tasks:
            self.add_widget(task, 1 + len(self.disabled_tasks))

    def reload_label(self):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute(f"SELECT label_name, priority FROM Labels WHERE ROWID = {self.rowid}")
        new_name = db.fetchone()
        self.label.update_name(str(new_name[0]))
        self.priority = new_name[1]
        database.close()

    def add_task(self, task):
        global which_label_global
        self.height += self.widget_height

        if task.active:
            self.disabled_tasks.append(task)
            task.opacity = .3
            if which_label_global != 'all':
                self.add_widget(self.disabled_tasks[-1], 1)
        else:
            self.tasks.append(task)
            if which_label_global != 'all':
                self.add_widget(self.tasks[-1], 1 + len(self.disabled_tasks))

    def add_photo(self, rowid, label_name):
        self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'camera_screen'
        self.parent.parent.parent.parent.parent.ids.camera_layout.build(rowid, label_name)


class TaskLabel(BoxLayout):
    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        self.info_window = None
        self.label_name = label
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'
        self.add_widget(Label(text=label, size_hint_x=.6))
        self.add_widget(Label(size_hint_x=.2))
        self.add_widget(MDIconButton(icon='trash-can-outline', icon_size=Window.size[1] / 40,
                                     center=(.5, .5), on_release=self.press, pos_hint={"center_x": .5, "center_y": .5}))

    def update_name(self, name):
        self.children[-1].text = name

    def remove(self, *args):
        self.parent.remove_disabled()
        self.info_window.dismiss()
        self.info_window = None

    def press(self, *args):
        self.info_window = MDDialog(
            text="Remove completed tasks from label: " + self.label_name + '?',
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x: self.info_window.dismiss()
                ),
                MDFlatButton(
                    text="REMOVE",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    on_release=self.remove
                ), ], )
        self.info_window.open()


class Task(BoxLayout):
    def __init__(self, label_name, label_id, active, priority, note, notification, eta, deadline, notification_time,
                 rowid, **kwargs):
        super().__init__(**kwargs)
        self.label_id = label_id
        self.label_name = label_name
        self.priority = priority
        self.eta = eta
        self.deadline = deadline
        self.note = note
        self.notification = notification
        self.notification_time = notification_time
        self.rowid = rowid
        self.active = active
        self.calendar = 0

        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'

        if type(self.active) == int:
            self.build_checkbox()
            self.build_rest()
            self.build_edit()

        elif type(self.active) == str:
            self.build_back_delete()
            self.build_rest()
            self.build_trash()

    def build_trash(self):
        self.trash = MDIconButton(icon='trash-can-outline', size_hint_x=.2, on_release=self.delete_permanent,
                                  pos_hint={'center_x': .5, 'center_y': .53})
        self.add_widget(self.trash)

    def build_back_delete(self):
        self.back_del = MDIconButton(icon='plus', size_hint_x=.2, on_release=self.back_delete,
                                     pos_hint={'center_x': .5, 'center_y': .53})
        self.add_widget(self.back_del)

    def build_checkbox(self):
        self.check_box = CheckBox(size_hint_x=.1, active=self.active,)
        self.check_box.bind(active=self.on_checkbox_active)
        self.add_widget(self.check_box)

    def build_edit(self):
        if self.notification:
            icon = 'bell'
        else:
            icon = 'bell-off-outline'
        time = str(self.eta)
        if self.eta != '-':
            time = '~'+time+'min'
        else:
            time = ""
        font_size = Window.size[1]/15/4
        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                MDIconButton(icon='dots-horizontal', on_release=self.edit, icon_size=font_size*1.5, size_hint=(.5, .5)),
                MDIconButton(icon=icon, icon_size=font_size*1.2, size_hint=(.5, .5), on_release=self.edit),
                size_hint_y=.5
            ),
            Button(text=time, size_hint_y=.2, font_size=font_size*0.8, halign='right', on_release=self.edit,
                   background_color=(0, 0, 0, 0)),
            Button(text=self.deadline, size_hint_y=.3, font_size=font_size*1.1, halign='right', on_release=self.edit,
                   background_color=(0, 0, 0, 0)),
            orientation='vertical', size_hint_x=.3
        ))

    def build_rest(self):
        global task_colors
        self.add_widget(Label(size_hint_x=.01))
        self.add_widget(MDIcon(icon='numeric-{}-box-outline'.format(self.priority), size_hint_x=.1,
                               text_color=task_colors[self.priority-1], theme_text_color='Custom',
                               pos_hint={"center_x": .5, "center_y": .53}))
        self.add_widget(Label(size_hint_x=.01))
        # if self.shape is None:
        if isinstance(self.note, str):
            self.add_widget(Label(text=self.note))
        else:
            buf1 = cv2.flip(self.note, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(self.note.shape[1], self.note.shape[0]), colorfmt='luminance')
            image_texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')

            self.add_widget(Image(texture=image_texture, pos_hint={'center_x': .5, 'center_y': .5}))

    def value(self):
        global order_by_global
        if order_by_global in ('category', 'priority'):
            return self.priority, self.deadline
        elif order_by_global == 'deadline':
            return self.deadline, self.priority

    def on_checkbox_active(self, instance, value):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        if value:
            db.execute(f"""
                            UPDATE Notes
                            SET active = 1
                            WHERE ROWID = {self.rowid};
                        """)
            database.commit()
            self.active = True
            self.parent.disable_task(self.rowid)
        else:
            db.execute(f"""
                            UPDATE Notes
                            SET active = 0
                            WHERE ROWID = {self.rowid};
                        """)
            database.commit()
            self.active = False
            self.parent.activate_task(self.rowid)
        database.close()

    def press(self, but):
        print(but.text)

    def edit(self, but):
        if not self.active:
            global which_label_global
            if which_label_global == 'all':
                self.parent.parent.parent.parent.parent.ids.nav_drawer.set_state("close")
                self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
                self.parent.parent.parent.parent.parent.ids.edit_screen.edit_task(self)
            else:
                self.parent.parent.parent.parent.parent.parent.ids.nav_drawer.set_state("close")
                self.parent.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
                self.parent.parent.parent.parent.parent.parent.ids.edit_screen.edit_task(self)

    def delete_permanent(self, *args):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute(f"""DELETE FROM Trash WHERE ROWID = {self.rowid}
             """)
        database.commit()
        database.close()
        self.parent.remove_task(self)

    def back_delete(self, *args):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        note = ''
        img = None
        shape = None
        if isinstance(self.note, str):
            note = self.note
        else:
            img = sqlite3.Binary(self.note)
            shape = np.array(img.shape)

        db.execute("""
                        INSERT INTO Notes (label_id, priority, deadline, note, image, active, eta, notification, 
                        notification_time, shape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (self.label_id, self.priority, self.deadline, note, img, 0, self.eta, self.notification,
                        self.notification_time, shape))

        database.commit()
        db.execute(""" SELECT ROWID, note FROM Notes ORDER BY ROWID DESC """)

        rowid = int(db.fetchone()[0])

        db.execute(f"SELECT label_name FROM Labels where ROWID = {self.label_id}")
        l_name = db.fetchone()[0]

        database.close()

        new_task = Task(l_name, self.label_id, 0, self.priority, self.note, self.notification, self.eta, self.deadline,
                        self.notification_time, rowid)
        self.parent.parent.parent.parent.parent.ids.main_screen.add_task(new_task)
        self.parent.parent.parent.parent.parent.ids.main_screen.labels[self.label_id].add_task(new_task)
        self.parent.parent.parent.parent.parent.ids.main_screen.update()

        self.delete_permanent()


class CustomNavigationDrawer(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload()

    def reload(self):
        self.clear_widgets()
        global TAG
        self.add_widget(MDNavigationDrawerHeader(title=TAG, padding=(0, 0, 0, 10)))  # source można dodać
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="calendar", on_release=self.print, text='bell'),
                                            text="Calendar", text_color=(.7, .7, .7, .5),
                                            on_release=self.calendar_open, divider=None))
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineRightIconListItem(IconRightWidget(icon="playlist-edit", on_release=self.edit_label, text='all',),
                                            text="Labels", on_release=self.press, divider=None))

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name, ROWID FROM Labels ORDER BY priority")
        items = db.fetchall()
        database.close()
        for el in items:
            self.add_widget(OneLineIconListItem(IconLeftWidget(icon="label-outline", on_release=self.edit_label, text=el[0],
                                                               id=str(el[1])),
                                            id=str(el[1]), text=el[0], text_color=(.7, .7, .7, .5),
                                            on_release=self.press, divider=None))

        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="plus", on_release=self.edit_label, text='Add Label'),
                                            text='Add Label', text_color=(.5, .5, .5, .5),
                                            on_release=self.edit_label, divider=None))
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="cog", on_release=self.print, text='cog'),
                                            text='Settings', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="trash-can-outline", on_release=self.trash_open, text='trash-can'),
                                            text='Trash', text_color=(.7, .7, .7, .5),
                                            on_release=self.trash_open, divider=None))
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="help-circle-outline", on_release=self.print, text='help'),
                                            text='Help', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))

    def print(self, butt):
        print(butt.text)

    def calendar_open(self, *args):
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        self.parent.parent.parent.ids.calendar_view.build_daily()
        self.parent.parent.parent.ids.screen_manager.current = 'calendar'

    def trash_open(self, *args):
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        self.parent.parent.parent.ids.trash_can_view.build()
        self.parent.parent.parent.ids.screen_manager.current = 'trash_can'

    def edit_label(self, but):
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        self.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        if but.text == 'all':
            self.parent.parent.parent.ids.edit_screen.edit_all_labels()
        elif but.text == 'Add Label':
            self.parent.parent.parent.ids.edit_screen.add_label()
        else:
            self.parent.parent.parent.ids.edit_screen.edit_label(int(but.id), but.text)

    def press(self, butt):
        self.parent.parent.parent.ids.screen_manager.current = 'screen'
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        if butt.text == 'Labels':
            self.parent.parent.parent.ids.main_screen.update('category', 'category')
        else:
            self.parent.parent.parent.ids.main_screen.update('priority', int(butt.id), 'asc')


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
        global which_label_global, order_by_global
        which_label_global = 'calendar'
        order_by_global = 'calendar'
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
        global task_colors
        self.md_bg_color = (task_colors[priority-1][0]*.3, task_colors[priority-1][1]*.3, task_colors[priority-1][2]*.3, 1)

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


class EditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_window = None
        self.remove_label_rowid = None
        self.images_list = None

        self.touched_id = None
        self.absolute_pos_0 = None
        self.widget_y_0 = None
        self.labels = []

        self.widget_height = Window.size[0]*.1
        self.edit_window = RelativeLayout()

        self.save_button = MDFlatButton(text='SAVE', size_hint_x=.35,
                                     md_bg_color=(0, 0, 0, 0), theme_text_color="Custom", text_color=(1, 1, 1, 1))
        self.cancel_button = MDFlatButton(text='CANCEL', size_hint_x=.35, font_size=10, on_release=self.exit,
                                     md_bg_color=(0, 0, 0, 0), theme_text_color="Custom", text_color=(1, 1, 1, .3))
        self.window = MDBoxLayout(
                    self.edit_window,
                    MDBoxLayout(
                        Label(size_hint_x=.3, color=(0, 0, 0, 0)),
                        self.cancel_button,
                        self.save_button,
                        size_hint_y=None, height=Window.size[0] * .07),
                    size_hint=(.8, None), height=Window.size[0] * .15, md_bg_color=(.15, .15, .15, 1),
                    pos_hint={"center_x": .5, "center_y": .5}, orientation='vertical',
                    spacing=self.widget_height*.1, padding=(self.widget_height*.3,0,self.widget_height*.3,0))
        self.add_widget(self.window)

    # edit label
    def edit_label(self, rowid, label_name):
        self.window.height += self.widget_height
        self.edit_window.add_widget(MDBoxLayout(
                                        MDTextField(text=label_name, # id='text_field',
                                            text_color_focus='white', line_color_focus='white',
                                            required=True),
                                        MDIconButton(id=label_name, text=str(rowid), icon='trash-can-outline',
                                                     size_hint_x=.1, pos_hint={"center_x": .5, "center_y": .75},
                                                     on_release=self.remove_dialog),
                                        id=str(rowid), size_hint_y=None, height=self.widget_height))
        self.save_button.text = "SAVE"
        self.save_button.bind(on_release=self.save_label)

    def save_label(self, *args):
        if self.edit_window.children[0].children[1].text:
            database = sqlite3.connect('databases/to_do.db')
            db = database.cursor()

            db.execute("""
                            UPDATE Labels
                            SET label_name = {}
                            WHERE ROWID = {};
                        """.format('"'+self.edit_window.children[0].children[1].text+'"', self.edit_window.children[0].id))
            database.commit()
            database.close()

            self.parent.parent.ids.md_list_nav_drawer.reload()
            self.parent.parent.ids.main_screen.reload_labels(int(self.edit_window.children[0].id),
                                                            self.edit_window.children[0].children[1].text)
            self.exit()
            self.save_button.unbind(on_release=self.save_label)
        else:
            if not self.info_window:
                self.info_window = Snackbar(text='Label name can not be empty!')
            self.info_window.open()
            Clock.schedule_once(self.close_info_window, 3)

    # add/remove label
    def add_label(self):
        self.window.height += self.widget_height
        self.edit_window.add_widget(MDTextField(text="", hint_text='Label Name:',
                                    hint_text_color_focus="white", text_color_focus='white',
                                    line_color_focus='white', required=True),)
        self.save_button.text = 'ADD'
        self.save_button.bind(on_release=self.add_additional_label)

    def add_additional_label(self, *args):
        if self.edit_window.children:
            if self.edit_window.children[0].text:
                database = sqlite3.connect('databases/to_do.db')
                db = database.cursor()

                db.execute(""" SELECT COUNT(ROWID) FROM Labels """)
                number_of_labels = db.fetchone()
                db.execute(" INSERT INTO Labels VALUES (" + str(number_of_labels[0]+2) + ", '" + self.edit_window.children[0].text + "'); ")
                database.commit()
                db.execute(f"SELECT ROWID from Labels WHERE label_name = '{self.edit_window.children[0].text}'")
                rowid = db.fetchone()[0]
                database.close()

                self.parent.parent.ids.md_list_nav_drawer.reload()
                self.parent.parent.ids.main_screen.reload_labels(int(rowid),
                                                                 self.edit_window.children[0].text, str(number_of_labels[0]+2))
                self.exit()
                self.save_button.unbind(on_release=self.add_additional_label)
            else:
                if not self.info_window:
                    self.info_window = Snackbar(text='Label name can not be empty!')
                self.info_window.open()
                Clock.schedule_once(self.close_info_window, 3)

    def remove_label(self, *args):
        self.close_info_window()
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        db.execute(" DELETE FROM Labels WHERE ROWID = " + str(self.remove_label_rowid))
        db.execute(" DELETE FROM Notes WHERE label_id = " + str(self.remove_label_rowid))
        database.commit()
        database.close()

        self.parent.parent.ids.main_screen.remove_label(int(self.remove_label_rowid))

        global which_label_global
        if which_label_global == self.remove_label_rowid:
            self.parent.parent.ids.main_screen.update('category', 'category')

        if len(self.edit_window.children) == 1:
            self.parent.parent.ids.md_list_nav_drawer.reload()
            self.exit()
            self.save_button.unbind(on_release=self.save_label)
        else:
            self.parent.parent.ids.md_list_nav_drawer.reload()
            self.edit_window.clear_widgets()
            self.window.height = Window.size[0] * .15
            self.save_button.unbind(on_release=self.save_label)
            self.edit_all_labels()

    # edit all labels
    def edit_all_labels(self):
        self.save_button.text = "SAVE"
        self.save_button.bind(on_release=self.save_labels)
        self.labels = []
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name, ROWID FROM Labels ORDER BY priority DESC")
        items = db.fetchall()
        database.close()
        height = 0
        for idx, item in enumerate(items):
            self.window.height += self.widget_height
            self.labels.append((MDBoxLayout(
                        MDIconButton(icon='dots-horizontal', size_hint_x=None, width=self.height * 1.5, text=str(item[1]),
                                     pos_hint={"center_x": .5, "center_y": .8}, ripple_alpha=0, on_press=self.dots_press,
                                     id='icon_but'),
                        MDTextField(text=item[0], text_color_focus='white', line_color_focus='white', required=True),
                        MDIconButton(id=item[0], text=str(item[1]), icon='trash-can-outline',
                                      size_hint_x=.1, pos_hint={"center_x": .5, "center_y": .75},
                                      on_release=self.remove_dialog, icon_size=self.widget_height*.5),
                        size_hint_y=None, height=self.widget_height, orientation='horizontal', pos=(0, height),
                        spacing=self.widget_height*.1), item[1]))
            self.edit_window.add_widget(self.labels[-1][0])
            height += self.widget_height

    def dots_press(self, but):
        for label_id in range(len(self.labels)):
            if self.labels[label_id][0].ids[str('icon_but')].text == but.text:
                self.touched_id = label_id
                self.widget_y_0 = but.parent.pos[1]
                return
        raise Exception("Didn't find label with text: {}".format(but.text))

    def on_touch_move(self, touch):
        if self.touched_id is not None:
            if self.absolute_pos_0 is None:
                self.absolute_pos_0 = touch.y
            else:
                pos_relative = touch.y - self.absolute_pos_0 + self.widget_y_0

                if 0 < pos_relative < self.widget_height * (len(self.labels) - 1):
                    if self.touched_id < len(self.labels) and pos_relative > self.widget_y_0 + self.widget_height*.75:
                        self.labels[self.touched_id+1][0].pos[1] -= self.widget_height
                        self.labels[self.touched_id], self.labels[self.touched_id+1] = self.labels[self.touched_id+1], self.labels[self.touched_id]
                        self.touched_id += 1
                        self.widget_y_0 += self.widget_height
                        self.absolute_pos_0 += self.widget_height
                    elif self.touched_id > 0 and pos_relative < self.widget_y_0 - self.widget_height*.75:
                        self.labels[self.touched_id - 1][0].pos[1] += self.widget_height
                        self.labels[self.touched_id], self.labels[self.touched_id - 1] = self.labels[self.touched_id - 1], self.labels[self.touched_id]
                        self.touched_id -= 1
                        self.widget_y_0 -= self.widget_height
                        self.absolute_pos_0 -= self.widget_height

                    self.labels[self.touched_id][0].y = pos_relative

                elif pos_relative < 0:
                    self.labels[self.touched_id][0].y = 0

                else:
                    self.labels[self.touched_id][0].y = self.widget_height * (len(self.labels) - 1)

    def on_touch_up(self, touch):
        if self.touched_id is not None:
            self.labels[self.touched_id][0].pos[1] = self.widget_y_0
            self.touched_id = None
            self.absolute_pos_0 = None

    def save_labels(self, *args):
        for label_tuple in self.labels:
            if not label_tuple[0].children[1].text:
                if not self.info_window:
                    self.info_window = Snackbar(text='Label name can not be empty!')
                self.info_window.open()
                Clock.schedule_once(self.close_info_window, 3)
                return

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        for idx, label_tuple in enumerate(self.labels, 1):
            db.execute("""
                        UPDATE Labels
                        SET priority = {}, label_name = {}
                        WHERE ROWID = {};
                    """.format(len(self.labels)-idx, '"'+label_tuple[0].children[1].text+'"', label_tuple[1]))
            database.commit()
            self.parent.parent.ids.main_screen.reload_labels(int(label_tuple[1]),
                                                             label_tuple[0].children[1].text)
        database.close()

        self.labels = []
        self.parent.parent.ids.md_list_nav_drawer.reload()
        self.parent.parent.ids.main_screen.update('category', 'category', 'asc')
        self.exit()

    # edit task
    def edit_task(self, task):
        self.save_button.text = "SAVE"
        self.save_button.bind(on_release=self.save_tasks)
        self.window.height += self.widget_height * 4
        self.window.size_hint_x = .9

        global task_colors
        if task.eta:
            eta = task.eta
        else:
            eta = "-"

        if task.calendar == 0:
            icon = 'bell-off-outline'
            notification = ""
            notification_time = ''
            not_disabled = True
            not_opacity = 0
        elif task.calendar == 1:
            icon = 'calendar'
            notification = task.notification
            notification_time = str(task.notification_time)
            not_disabled = False
            not_opacity = 1
        else:
            icon = 'bell'
            notification = task.notification
            notification_time = str(task.notification_time)
            not_disabled = False
            not_opacity = 1

        if task.deadline:
            deadline = task.deadline
        else:
            deadline = '-'

        note_widget = None
        if isinstance(task.note, str):
            note_widget = MDTextField(
                text=task.note, line_color_focus=(1, 1, 1, 1), text_color_focus=(1, 1, 1, 1))
        else:
            buf1 = cv2.flip(task.note, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(task.note.shape[1], task.note.shape[0]), colorfmt='luminance')
            image_texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')

            note_widget = Image(texture=image_texture, pos_hint={'center_x': .5, 'center_y': .5},
                                size_hint_y=None, height=self.widget_height*1.5)

        self.edit_window.add_widget(MDBoxLayout(
            MDBoxLayout(
                Label(size_hint_x=.2, text='priority:'),
                MDIconButton(id='priority', text=str(task.priority), icon=f'numeric-{task.priority}-box-outline',
                             size_hint_x=.2, text_color=task_colors[task.priority-1], theme_text_color='Custom',
                             on_release=lambda x: self.priority_menu.open(), pos_hint={"center_x": 0, "center_y": .6},
                             md_bg_color=(1, 1, 1, .03)),
                Label(size_hint_x=.01),
                MDFlatButton(id='date', size_hint_x=.3, text=notification, pos_hint={"center_x": 0, "center_y": .6},
                      disabled=not_disabled, font_size=self.widget_height*.35, md_bg_color=(1, 1, 1, .03),
                      opacity=not_opacity, on_release=lambda x: self.show_date_picker('notification')),
                MDFlatButton(id='time', size_hint_x=.1, text=notification_time, pos_hint={"center_x": 0, "center_y": .6},
                        disabled=not_disabled, font_size=self.widget_height*.35, md_bg_color=(1, 1, 1, .03),
                        opacity=not_opacity, on_release=lambda x: self.show_time_picker()),
                MDIconButton(text='notification', size_hint_x=.1, pos_hint={"center_x": 0, "center_y": .6},
                             md_bg_color=(1, 1, 1, .03), on_release=lambda x: self.notification_menu.open(),
                             icon=f"{icon}", icon_size=self.widget_height*.5),
                size_hint_y=None, height=self.widget_height*.7, orientation='horizontal'),
            note_widget,
            MDBoxLayout(
                MDFlatButton(id=f"{task.label_id}", text=task.label_name, size_hint_x=.4,
                             on_release=lambda x: self.label_name_menu.open(), md_bg_color=(1, 1, 1, .03)),
                Label(size_hint_x=.25),
                Label(text='eta: ', size_hint_x=.1, pos_hint={"center_x": 0, "center_y": .75}),
                TextInput(text=f"{eta}", size_hint=(.2, None), background_color=(1, 1, 1, .03),
                            foreground_color=(1, 1, 1, 1), multiline=False, font_size=self.widget_height*.4,
                            height=self.widget_height, cursor_color=(1, 1, 1, 1), pos_hint={"center_x": 0, "center_y": .6}),
                Label(text='min', size_hint_x=.1, pos_hint={"center_x": 0, "center_y": .75}),
                size_hint_y=None, height=self.widget_height*.7, orientation='horizontal', ),
            MDBoxLayout(
                Label(text='active: ', size_hint_x=.2),
                CheckBox(size_hint_x=.1, active=task.check_box.active, pos_hint={"center_x": 1, "center_y": .45},
                         disabled=True),
                Label(size_hint_x=.2),
                Label(size_hint_x=.2, text='deadline:', pos_hint={"center_x": 0, "center_y": .5}),
                MDFlatButton(size_hint_x=.4, text=deadline, pos_hint={"center_x": 0, "center_y": .5},
                             font_size=self.widget_height * .35, md_bg_color=(1, 1, 1, .03),
                             on_release=lambda x: self.show_date_picker('deadline'), id=str(task.rowid)),
                size_hint_y=None, height=self.widget_height, orientation='horizontal'),
            size_hint_y=None, height=self.widget_height*4.5, orientation='vertical'))

        priority_items = []
        for number, color in enumerate(task_colors, 1):
            priority_items.append({
                "viewclass": "MDIconButton",
                "icon": f'numeric-{str(number)}-box-outline',
                "icon_size": self.widget_height*.7,
                "text_color": color,
                "theme_text_color": 'Custom',
                "on_release": lambda x=number: self.update_priority(x)
            })
        self.priority_menu = MDDropdownMenu(caller=self.edit_window.children[0].children[-1].children[-2],
                                            items=priority_items, max_height=self.widget_height*5.8)

        label_name_items = []
        tuple_ln_rowid = get_from_db.get_label_names('to_do')
        for label_name, rowid in tuple_ln_rowid:
            label_name_items.append({
                "viewclass": "MDFlatButton",
                "text": f"{label_name}",
                "on_release": lambda x=label_name, y=rowid: self.update_label_name(x, y)
            })
        #print(self.edit_window.children[0].children[-3].children[-1])
        self.label_name_menu = MDDropdownMenu(caller=self.edit_window.children[0].children[-3].children[-1],
                                            items=label_name_items, width_mult=2,
                                            max_height=min(self.widget_height*5.8, self.widget_height*1.1*len(tuple_ln_rowid)),)

        notification_items = []
        for icon in ['bell-off-outline', 'bell']:
            notification_items.append({
                "viewclass": "MDIconButton",
                "icon": icon,
                "text_color": (1, 1, 1, 1),
                "icon_size": self.widget_height * .5,
                "on_release": lambda x=icon, y=task: self.update_notification(x, y)
            })
        #print(self.edit_window.children[0].children[-1].children[0].text)
        self.notification_menu = MDDropdownMenu(caller=self.edit_window.children[0].children[-1].children[0],
                                            width_mult=.5, items=notification_items, max_height=self.widget_height*2.8,
                                            position='center')

    def add_task(self, label_id, label_name):
        self.new_task = Task(label_name, label_id, 0, 1, '', '', '-', date.today().strftime('20%y-%m-%d'), '', -1)
        self.edit_task(self.new_task)

    def add_img_tasks(self, images_list=None, label_id=None, label_name=None):
        if images_list:
            self.images_list = images_list
            self.label_id = label_id
            self.label_name = label_name
        if self.images_list:
            self.new_task = Task(self.label_name, self.label_id, 0, 1, self.images_list[0], '', '-', date.today().strftime('20%y-%m-%d'), '', -1)
            del self.images_list[0]
            self.edit_task(self.new_task)
        else:
            self.exit()

    def show_date_picker(self, text):
        self.date_dialog = MDDatePicker(helper_text=text, text_button_color="lightgrey",)
        self.date_dialog.bind(on_save=self.pick_data)
        self.date_dialog.open()

    def show_time_picker(self): #   input_field_text_color
        self.date_dialog = MDTimePicker(text_button_color="lightgrey",)
        self.date_dialog.bind(on_save=self.pick_time)
        self.date_dialog.set_time(datetime.now())
        self.date_dialog.open()

    def pick_time(self, instance, value, *args):
        self.edit_window.children[0].children[-1].children[1].text = value.strftime("%H:%M")

    def pick_data(self, instance, value, *args):
        if str(value) >= date.today().strftime("20%y-%m-%d"):
            if self.date_dialog.helper_text == 'notification':
                self.edit_window.children[0].children[-1].children[2].text = str(value)
            elif self.date_dialog.helper_text == 'deadline':
                self.edit_window.children[0].children[0].children[0].text = str(value)
        else:
            if not self.info_window:
                self.info_window = Snackbar(text='Date can not be earlier than today!')
            self.info_window.open()
            Clock.schedule_once(self.close_info_window, 3)
            return
        #print(value, date.today().strftime("20%y-%m-%d"))

    def update_priority(self, new_priority):
        self.edit_window.children[0].children[-1].children[-2].icon = f'numeric-{new_priority}-box-outline'
        self.edit_window.children[0].children[-1].children[-2].text = str(new_priority)
        global task_colors
        self.edit_window.children[0].children[-1].children[-2].text_color = task_colors[new_priority-1]
        self.priority_menu.dismiss()

    def update_label_name(self, label_name, rowid):
        self.edit_window.children[0].children[-3].children[-1].text = label_name
        self.edit_window.children[0].children[-3].children[-1].id = f"{rowid}"
        self.label_name_menu.dismiss()

    def update_notification(self, icon, task):
        self.notification_menu.dismiss()
        if icon == 'bell':
            if task.notification:
                notification = task.notification
                time = task.notification_time
            else:
                notification = date.today().strftime("20%y-%m-%d")
                time = datetime.now().strftime("%H:%M")
            self.edit_window.children[0].children[-1].children[2].text = notification
            self.edit_window.children[0].children[-1].children[2].disabled = False
            self.edit_window.children[0].children[-1].children[2].opacity = 1

            self.edit_window.children[0].children[-1].children[1].text = time
            self.edit_window.children[0].children[-1].children[1].disabled = False
            self.edit_window.children[0].children[-1].children[1].opacity = 1

            self.edit_window.children[0].children[-1].children[0].icon = 'bell'
        else:
            self.edit_window.children[0].children[-1].children[2].text = ""
            self.edit_window.children[0].children[-1].children[2].disabled = True
            self.edit_window.children[0].children[-1].children[2].opacity = 0

            self.edit_window.children[0].children[-1].children[1].text = ""
            self.edit_window.children[0].children[-1].children[1].disabled = True
            self.edit_window.children[0].children[-1].children[1].opacity = 0

            self.edit_window.children[0].children[-1].children[0].icon = 'bell-off-outline'

    def save_tasks(self, *args):
        rowid = int(self.edit_window.children[0].children[0].children[0].id)
        if rowid == -1:
            self.save_new_task()
            return

        label_id = int(self.edit_window.children[0].children[1].children[-1].id)
        for el in self.edit_window.children[0].children[1].children[1].text:
            if el < str(0) or el > str(9):
                if self.edit_window.children[0].children[1].children[1].text != '-':
                    self.info_window = Snackbar(text='ETA incorrect! Set to NULL')
                    self.info_window.open()
                    Clock.schedule_once(self.close_info_window, 3)
                    self.edit_window.children[0].children[1].children[1].text = '-'
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        db.execute(f"""
                        UPDATE Notes
                        SET label_id = {label_id},
                            priority = {self.edit_window.children[0].children[3].children[-2].text},
                            deadline = '{self.edit_window.children[0].children[0].children[0].text}',
                            eta = '{self.edit_window.children[0].children[1].children[1].text}',
                            notification = '{self.edit_window.children[0].children[3].children[2].text}',
                            notification_time = '{self.edit_window.children[0].children[3].children[1].text}'
                        WHERE ROWID = {rowid};
                    """)
        if isinstance(self.edit_window.children[0].children[2], MDTextField):
            db.execute(f"""
                            UPDATE Notes
                            SET note = '{self.edit_window.children[0].children[2].text}'
                            WHERE ROWID = {rowid};
                        """)
        database.commit()
        database.close()

        global which_label_global
        if which_label_global != 'calendar':
            self.parent.parent.ids.main_screen.update()
        else:
            self.parent.parent.ids.calendar_view.reload_task(rowid)
        self.parent.parent.ids.main_screen.reload_task(rowid)
        self.exit()

    def save_new_task(self):
        label_id = int(self.edit_window.children[0].children[1].children[-1].id)
        for el in self.edit_window.children[0].children[1].children[1].text:
            if el < str(0) or el > str(9):
                if self.edit_window.children[0].children[1].children[1].text != '-':
                    self.info_window = Snackbar(text='ETA incorrect! Set to NULL')
                    self.info_window.open()
                    Clock.schedule_once(self.close_info_window, 3)
                    self.edit_window.children[0].children[1].children[1].text = '-'
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        note = ''
        img = None
        shape = None
        if isinstance(self.edit_window.children[0].children[2], MDTextField):
            note = self.edit_window.children[0].children[2].text
        else:
            img = sqlite3.Binary(self.new_task.note)
            shape = np.array(img.shape)

        db.execute("""
                INSERT INTO Notes (label_id, priority, deadline, note, image, active, eta, notification,
                notification_time, shape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (label_id, self.edit_window.children[0].children[3].children[-2].text,
                      self.edit_window.children[0].children[0].children[0].text, note, img, 0,
                      self.edit_window.children[0].children[1].children[1].text,
                      self.edit_window.children[0].children[3].children[2].text,
                      self.edit_window.children[0].children[3].children[1].text, shape))

        database.commit()

        db.execute("""SELECT ROWID, note FROM Notes ORDER BY ROWID DESC """)
        rowid = int(db.fetchone()[0])

        self.new_task.rowid = rowid
        self.parent.parent.ids.main_screen.add_task(self.new_task)
        self.parent.parent.ids.main_screen.reload_task(rowid)
        self.new_task = None

        #self.parent.parent.ids.main_screen.update()
        self.exit()

    # close window
    def remove_dialog(self, but):
        self.remove_label_rowid = int(but.text)
        if not self.info_window:
            self.info_window = MDDialog(
                text="Remove label: " + but.id + '?',
                buttons=[
                   MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        on_release=self.close_info_window
                   ),
                   MDFlatButton(
                        text="REMOVE",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        on_release=self.remove_label
                   ), ], )
        self.info_window.open()

    def close_info_window(self, *args):
        if self.info_window:
            self.info_window.dismiss()
            self.info_window = None

    def exit(self, *args):
        self.edit_window.clear_widgets()
        self.window.height = Window.size[0] * .15
        self.window.size_hint_x = .8

        if self.images_list:
            self.add_img_tasks()
        else:
            self.save_button.unbind(on_release=self.save_tasks)
            self.save_button.unbind(on_release=self.save_labels)
            self.save_button.unbind(on_release=self.save_label)
            global which_label_global
            if which_label_global == 'calendar':
                self.parent.current = 'calendar'
            else:
                self.parent.current = 'screen'


class TrashCanView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.clear_widgets()
        self.tasks = []

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("""SELECT priority, deadline, note, eta, notification, notification_time, deleted_date, ROWID, 
             label_id, image, shape
             FROM Trash 
             ORDER BY deleted_date""")
        items = db.fetchall()

        for i in items: # 10
            if i[10] is None:
                self.tasks.append(Task(None, i[8], i[6], i[0], i[2], i[4], i[3], i[1], i[5], i[7]))
            else:
                shape = np.frombuffer(i[10], dtype='int32')
                img = np.frombuffer(i[9], dtype=np.uint8)
                img.shape = shape
                self.tasks.append(Task(None, i[8], i[6], i[0], img, i[4], i[3], i[1], i[5], i[7]))

            self.add_widget(self.tasks[-1])

        database.close()

    def remove_task(self, task):
        self.remove_widget(task)
        self.tasks.remove(task)


class CameraLayout(MDFloatLayout):
    def build(self, rowid, label_name):
        self.rowid = rowid
        self.label_name = label_name
        self.md_bg_color = (0, 0, 0, 1)
        icon_size = Window.size[0]/8
        self.add_widget(MDIconButton(pos_hint={'center_x': .5}, icon='camera-outline', size_hint=(None, None),
                               on_release=lambda x: self.take_photo(), icon_size=icon_size,
                               md_bg_color=(32/255, 3/255, 252/255, 1)))
        self.camera = TaskCamera(play=True)
        self.add_widget(self.camera)

    def take_photo(self):
        self.camera.play = False
        self.clear_widgets()

        self.edit_grid = EditPhoto(self.camera.texture, md_bg_color=(1,1,1,.1), size_hint=(1, .8),
                                   pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(self.edit_grid)

        self.add_widget(MDBoxLayout(
            MDFlatButton(text='CANCEL', on_release=lambda x: self.exit(), size_hint_min=(None, None), size_hint=(.5, 1),
                         font_size=Window.size[1]*.03),
            MDFlatButton(text='SAVE', on_release=self.save_cut, size_hint_min=(None, None), size_hint=(.5, 1),
                        font_size=Window.size[1] * .03),
            orientation='horizontal', size_hint=(1, .1)
        ))

    def save_cut(self, *args):
        self.children[0].children[0].unbind(on_release=self.save_cut)
        self.children[0].children[0].bind(on_release=self.save_all)

        self.add_widget(MDBoxLayout(
            MDIconButton(icon='minus', on_release=lambda x: self.edit_grid.remove_horizontal(),
                         size_hint_min=(None, None), size_hint=(.5, 1), icon_size=Window.size[1]*.06),
            MDIconButton(icon='plus', on_release=lambda x: self.edit_grid.add_horizontal(),
                         size_hint_min=(None, None), size_hint=(.5, 1), icon_size=Window.size[1] * .06),
            orientation='horizontal', size_hint=(1, .1), pos_hint={'top': 1}))

        self.edit_grid.save_cut()

    def save_all(self, *args):
        images = self.edit_grid.save_all()
        self.clear_widgets()
        self.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        self.parent.parent.parent.ids.edit_screen.add_img_tasks(images, self.rowid, self.label_name)

    def exit(self):
        self.clear_widgets()
        self.parent.parent.parent.ids.screen_manager.current = 'screen'


class EditPhoto(MDFloatLayout):
    def __init__(self, texture, **kwargs):
        super().__init__(**kwargs)
        self.add_photo('cut', texture)
        self.max_lines = 15
        self.lines_addition = 50

    def add_photo(self, usage, texture):  # texture.size = width / height
        self.image1 = cv2.imread('images/x_cut.jpg')
        # plt.imshow(self.image1, 'gray') luminance
        # plt.axis('off')
        # plt.show()
        #
        # buf1 = cv2.flip(self.image1, 0)
        # buf = buf1.tostring()
        # image_texture = Texture.create(size=(self.image1.shape[1], self.image1.shape[0]), colorfmt='bgr')
        # image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.image1 = texture
        if usage == 'cut':
            self.image1 = rotate_image_right(self.image1)
        #print(texture.size)

        self.photo = Image(texture=self.image1, size_hint=(.9, .9), pos_hint={'center_x': .5, 'center_y': .5})

        print(self.image1)

        self.add_widget(self.photo)

        img_ratio = self.image1.size[0]/self.image1.size[1]  # width / height
        real_ratio = Window.size[0]/(Window.size[1]*.8)

        if img_ratio > real_ratio:
            self.im_width = min(Window.size[0]*.9, self.image1.size[0])
            self.im_height = self.im_width/img_ratio

        else:
            self.im_height = min(Window.size[1]*.8*.9, self.image1.size[1])
            self.im_width = self.im_height * img_ratio

        self.x0 = (Window.size[0]/2) - (self.im_width/2)
        self.xmax = (Window.size[0] / 2) + (self.im_width / 2)

        self.y0 = (Window.size[1]/2) - (self.im_height/2)
        self.ymax = (Window.size[1]/2) + (self.im_height/2)

        self.line_idx = None

        if usage == 'cut':
            self.lines_vertical()
        elif usage == 'divide':
            self.lines_horizontal()

    def lines_horizontal(self):
        return
        img = cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY)

        # plt.imshow(image_bin, 'gray')
        # plt.axis('off')
        # plt.show()

        (h, w) = img.size[:2]
        width = 1000
        r = width / float(w)
        dim = (width, int(h * r))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        nr = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        image_bin = np.where(img < nr[0], 0, 1)

        ratio_break = []
        first_white = -1
        for curr_line in range(image_bin.size[0]):
            for col in range(image_bin.size[1]):
                if image_bin[curr_line][col] == 0:  # if black pixel
                    if first_white > 0:
                        curr_ratio = ((curr_line - first_white) / 2 + first_white) / image_bin.shape[0]
                        if ratio_break == [] or (curr_ratio - ratio_break[-1] > .05):
                            ratio_break.append(curr_ratio)
                        first_white = -1
                    break
            else:
                if first_white == -1:
                    first_white = curr_line

        for ratio in ratio_break:
            self.add_horizontal(ratio)

    def add_horizontal(self, ratio=1):
        if len(self.lines) < self.max_lines:
            y = self.ymax - ((self.ymax-self.y0)*ratio)
            self.lines.append(CutLine('horizontal', self.im_width, y=y))
            self.add_widget(self.lines[-1])

    def remove_horizontal(self):
        if self.lines:
            self.remove_widget(self.lines[-1])
            del self.lines[-1]

    def lines_vertical(self):
        self.lines = [CutLine('vertical', self.im_height, x=self.x0),
                      CutLine('vertical', self.im_height, x=self.xmax)]
        self.add_widget(self.lines[0])
        self.add_widget(self.lines[1])

    def save_cut(self):
        ratio_x = []
        for line in self.lines:
            ratio_x.append((line.x - self.x0) / self.im_width)

        image = texture_to_ndarray(self.image1)
        image = image[0:int(self.image1.size[0]), int(self.image1.size[1] * ratio_x[0]):int(self.image1.size[1] * ratio_x[1])]
        texture_cut = ndarray_to_texture(image)

        self.clear_widgets()
        self.image1 = None
        self.lines = []
        self.add_photo('divide', texture_cut)

    def save_all(self):
        task_images = []
        prev_ratio = 0
        self.image1 = cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY)

        (h, w) = self.image1.shape[:2]
        width = 1000
        r = width / float(w)
        dim = (width, int(h * r))
        self.image1 = cv2.resize(self.image1, dim, interpolation=cv2.INTER_AREA)

        nr = cv2.threshold(self.image1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        for row in range(self.image1.shape[0]):
            for col in range(self.image1.shape[1]):
                if self.image1[row][col] > nr[0]:
                    self.image1[row][col] = 0
                else:
                    self.image1[row][col] = 255

        for line in self.lines:
            curr_ratio = (self.ymax - line.y) / self.im_height
            img_cut = self.image1[int(self.image1.shape[0] * prev_ratio):int(self.image1.shape[0] * curr_ratio),  \
                                                                                                0:int(self.image1.shape[1])]
            task_images.append(img_cut)
            prev_ratio = curr_ratio

        img_cut = self.image1[int(self.image1.shape[0] * prev_ratio):self.image1.shape[0], 0:int(self.image1.shape[1])]
        task_images.append(img_cut)

        return task_images

    def on_touch_down(self, touch):
        for i in range(len(self.lines)):
            if (self.lines[i].x-self.lines[i].w_size[0]) <= touch.x <= self.lines[i].x+self.lines[i].w_size[0] \
                    and (self.lines[i].y-self.lines[i].w_size[1]) <= touch.y <= self.lines[i].y+self.lines[i].w_size[1]:
                self.line_idx = i

    def on_touch_up(self, touch):
        self.line_idx = None

    def on_touch_move(self, touch):
        if self.line_idx is not None:
            line = self.lines[self.line_idx]
            if line.orientation == 'vertical':
                if touch.x > self.xmax:
                    touch.x = self.xmax
                elif touch.x < self.x0:
                    touch.x = self.x0
                line.x = touch.x
                line.update_pos(touch.x)

                if self.line_idx > 0 and self.lines[self.line_idx-1].x > line.x:
                    self.lines[self.line_idx], self.lines[self.line_idx - 1] = self.lines[self.line_idx - 1], \
                                                                             self.lines[self.line_idx]
                    self.line_idx -= 1
                elif self.line_idx < len(self.lines)-1 and self.lines[self.line_idx+1].x < line.x:
                    self.lines[self.line_idx], self.lines[self.line_idx + 1] = self.lines[self.line_idx + 1], \
                                                                               self.lines[self.line_idx]
                    self.line_idx += 1
            else:
                if touch.y > self.ymax:
                    touch.y = self.ymax
                elif touch.y < self.y0:
                    touch.y = self.y0
                line.y = touch.y
                line.update_pos(touch.y)

                if self.line_idx > 0 and self.lines[self.line_idx-1].y < line.y:
                    self.lines[self.line_idx], self.lines[self.line_idx - 1] = self.lines[self.line_idx - 1], \
                                                                             self.lines[self.line_idx]
                    self.line_idx -= 1
                elif self.line_idx < len(self.lines)-1 and self.lines[self.line_idx+1].y > line.y:
                    self.lines[self.line_idx], self.lines[self.line_idx + 1] = self.lines[self.line_idx + 1], \
                                                                               self.lines[self.line_idx]
                    self.line_idx += 1


class CutLine(MDBoxLayout):
    def __init__(self, orientation, size, **kwargs):
        super().__init__(**kwargs)
        # radius = 3
        radius = 5
        size += 36
        self.orientation = orientation
        self.circle = [None, None]
        if orientation == 'vertical':
            size += 9
            self.y = Window.size[1]*.1
            if Window.size[1]*.8 > size:
                self.w_size = (radius*1.1, size)
                self.y += (Window.size[1]*.8 - size)/2
            else:
                self.w_size = (radius*1.1, Window.size[1]*.8)

            self.size = self.w_size

            p1 = (self.x, self.y+radius*2)
            p2 = (self.x, self.y+self.height-(2*radius))
            with self.canvas:
                Color(1, 0, 0)
                self.line = Line(points=[p1[0], p1[1]+radius, p2[0], p2[1]-radius], width=radius * .2)
                self.circle[0] = Line(circle=(p1[0], p1[1], radius),)
                self.circle[1] = Line(circle=(p2[0], p2[1], radius),)

        else:
            if Window.size[0] > size:
                self.w_size = (size, radius*1.1)
                self.x += (Window.size[0] - size)/2
            else:
                self.w_size = (Window.size[0], radius*1.1)

            self.size = self.w_size

            p1 = (self.x+radius*2, self.y)
            p2 = (self.x+self.width-(2*radius), self.y)
            with self.canvas:
                Color(1, 0, 0)
                self.line = Line(points=[p1[0]+radius, p1[1], p2[0]-radius, p2[1]], width=radius * .2)
                self.circle[0] = Line(circle=(p1[0], p1[1], radius),)
                self.circle[1] = Line(circle=(p2[0], p2[1], radius),)

    def update_pos(self, pos):
        radius = 5
        if self.orientation == 'vertical':
            self.line.points = (pos, self.line.points[1], pos, self.line.points[3])
            for circle in self.circle:
                circle.circle = (pos, circle.circle[1], circle.circle[2])
        else:
            self.line.points = (self.line.points[0], pos, self.line.points[2], pos)
            for circle in self.circle:
                circle.circle = (circle.circle[0], pos, circle.circle[2])

    def get_pos(self):
        if self.orientation == 'vertical':
            return self.x + 3
        else:
            return self.y + 3


class TaskCamera(Camera):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=(-90), origin=[Window.size[0]/2, Window.size[1]/2])
        with self.canvas.after:
            PopMatrix()
        #self.resolution = Window.size


def rotate_image_right(texture):
    is_texture = False
    image = texture
    if isinstance(texture, Texture):
        is_texture = True

        image = np.frombuffer(texture.pixels, dtype='int32')

        image = image.reshape(int(texture.size[1]), texture.size[0])
        image = image[0:int(image.shape[0]), 0:int(image.shape[1])]

    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    if is_texture:
        image = ndarray_to_texture(image)
        image.flip_vertical()

    return image


def texture_to_ndarray(texture):
    image = np.frombuffer(texture.pixels, dtype='int32')
    image = image.reshape(texture.size[1], texture.size[0])

    return image


def ndarray_to_texture(image):
    buf1 = cv2.flip(image, 0)
    buf = buf1.tostring()
    image_texture = Texture.create(size=(image.shape[1], image.shape[0]))
    image_texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')

    return image_texture
