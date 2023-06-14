from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, NoTransition, FadeTransition, ScreenManager
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from time import sleep
from datetime import date
from datetime import datetime
import sqlite3
import time

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget, OneLineRightIconListItem, \
    ILeftBody, ILeftBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawerHeader, \
    MDNavigationDrawerLabel, MDNavigationDrawer, MDNavigationDrawerDivider, MDNavigationDrawerItem
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.widget import MDWidget

from layouts.notebook import Notebook
import include.get_from_db as get_from_db

task_colors = [(1, 0, 0, .9), (245 / 255, 118 / 255, 39 / 255, 0.8), (245 / 255, 217 / 255, 39 / 255, 0.8),
                   (47 / 255, 151 / 255, 33 / 255, 0.8)]

menu_button_ratio = 8
side_menu_button_ratio = 15
m_size_global = Window.size[0] / menu_button_ratio
s_butt_size_global = Window.size[1] / side_menu_button_ratio
TAG = 'TO DO'


class ToDoList(MDNavigationLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global TAG
        self.items = TAG

    def get_tag(self):
        return self.tag


class NavigationDrawerScreenManager(MDScreenManager): #  TODO tu musi być screenmanager żeby nie było laga
    pass


class MainView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.labels = {rowid: LabelLayout(), }
        self.labels = {}
        self.tasks = []
        self.order_by = 'priority'
        self.which_label = 'category'

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT ROWID, label_name FROM Labels ORDER BY priority")
        labels = db.fetchall()
        for label in labels:
            # t_start = time.perf_counter()
            self.labels[label[0]] = LabelLayout(label[0], label[1])
            self.add_widget(self.labels[label[0]])
            db.execute("""SELECT N.active, N.priority, N.note, N.notification, N.eta, N.deadline, N.notification_time,
                        N.ROWID
            FROM Labels AS L LEFT JOIN Notes AS N ON L.ROWID = N.label_id
            WHERE N.label_id = {} ORDER BY N.active, N.priority, N.deadline""".format(label[0]))
            items = db.fetchall()
            # t_stop = time.perf_counter()
            # print("Czas obliczeń:", "{:.7f}".format(t_stop - t_start))

            for i in items:
                self.tasks.append(Task(label[1], str(label[0]), i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
                self.labels[label[0]].add_task(self.tasks[-1])

        database.close()

    def add_task(self, task):
        self.tasks.append(task)
        self.labels[task.label_id].add_task(self.tasks[-1])

    def reload_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                database = sqlite3.connect('databases/to_do.db')
                db = database.cursor()
                db.execute(f"""SELECT active, priority, note, notification, eta, deadline, notification_time,
                        ROWID, label_id FROM Notes WHERE ROWID = {rowid}""")
                it = db.fetchone()

                db.execute(f"""SELECT label_name FROM Labels WHERE ROWID = {it[8]}""")
                lt = db.fetchone()

                self.tasks[i] = Task(lt[0], it[8], it[0], it[1], it[2], it[3], it[4], it[5], it[6], it[7])

                if int(self.tasks[i].label_id) != it[8]:
                    self.labels[int(self.tasks[i].label_id)].remove_task(rowid)
                    self.labels[it[8]].add_task(self.tasks[i])
                else:
                    self.labels[it[8]].remove_task(rowid)
                    self.labels[it[8]].add_task(self.tasks[i])

                self.labels[it[8]].sort_label_layout()

                database.close()
                return

    # zmienia label_name / dodaje nową label_name
    def reload_labels(self, rowid, label_name):
        if rowid in self.labels.keys():
            self.labels[rowid].reload_label()
        else:
            self.labels[rowid] = LabelLayout(rowid, label_name)
            if self.which_label == 'category':
                self.add_widget(self.labels[rowid])
            elif self.which_label != 'all':
                self.update(self.order_by, rowid)

    def remove_label(self, rowid):
        for task in self.tasks:
            if task.label_id == rowid:
                self.tasks.remove(task)
        self.remove_widget(self.labels[rowid])
        del self.labels[rowid]

    def sort_labels(self):
        print('sort_labels')

    def update(self, order_by=None, which_label=None):
        self.clear_widgets()
        if order_by is None:
            order_by = self.order_by
        if which_label is None:
            which_label = self.which_label

        # if order_by != self.order_by:
        #     pass  # TODO tu trzeba sortowanie
        if which_label == 'all':  # dodaje po kolei z self.tasks
            # sort self.tasks by order_by
            for task in self.tasks:
                self.add_widget(task)
        elif which_label == 'category':
            # labels_keys = sort self.labels.keys() by priority
                # sort self.labels[x].tasks by order_by
            for key in self.labels.keys():  # tu labels_keys
                self.add_widget(self.labels[key])
        else:
            # if self.labels[which_label].order_by != order_by
                # sort self.labels[which_label] by order_by
            self.add_widget(self.labels[which_label])

        self.order_by = order_by
        self.which_label = which_label


class LabelLayout(MDBoxLayout):
    def __init__(self, rowid, label_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None

        self.rowid = rowid
        self.order_by = 'priority'
        self.widget_height = Window.size[1] / 13
        self.height = self.widget_height * 1.65

        self.tasks = []
        self.label = TaskLabel(label_name)
        self.add_widget(self.label)
        self.add_widget(MDRectangleFlatIconButton(icon='plus', text='Add Task', on_release=lambda x: self.add_window(),
                size_hint=(1, None), text_color=(1, 1, 1, 1), line_color=(1, 1, 1, 0),
                icon_color=(1, 1, 1, 1), md_bg_color=(.1, .1, .1, .5)))

    def add_window(self):
        self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        self.parent.parent.parent.parent.parent.ids.edit_screen.add_task(self.rowid, self.label.label_name)

    def remove_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                self.remove_widget(self.tasks[i])
                del self.tasks[i]
                self.height -= self.widget_height
                return

    def sort_label_layout(self, order_by=None):
        if order_by is None:
            order_by = self.order_by
        # sort self.tasks by order_by
        print(f'sort label {self.rowid} by {order_by}')

    def reload_label(self):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute(f"SELECT label_name FROM Labels WHERE ROWID = {self.rowid}")
        new_name = db.fetchone()
        self.label.update_name(str(new_name[0]))
        database.close()

    def add_task(self, task):
        self.height += self.widget_height
        self.tasks.append(task)
        self.add_widget(self.tasks[-1], 1)


class TaskLabel(BoxLayout):
    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
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

    def press(self, but):
        print(but.icon)


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

        global task_colors
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'
        self.check_box = CheckBox(size_hint_x=.1, active=active)
        self.add_widget(self.check_box)
        self.add_widget(Label(size_hint_x=.01))
        self.add_widget(MDIcon(icon='numeric-{}-box-outline'.format(priority), size_hint_x=.1,
                               text_color=task_colors[priority-1], theme_text_color='Custom',
                               pos_hint={"center_x": .5, "center_y": .53}))
        self.add_widget(Label(text=note))
        if notification:
            icon = 'bell'
        else:
            icon = 'bell-off-outline'
        time = str(eta)
        if eta != '-':
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
            Button(text=deadline, size_hint_y=.3, font_size=font_size*1.1, halign='right', on_release=self.edit,
                   background_color=(0, 0, 0, 0)),
            orientation='vertical', size_hint_x=.3
        ))

    def move(self):
        #pos = self.pos_hint['center_x']
        self.children[0], self.children[1] = self.children[1], self.children[0]
        self.children[1], self.children[2] = self.children[2], self.children[1]

    def press(self, but):
        print(but.text)

    def edit(self, but):
        self.parent.parent.parent.parent.parent.parent.ids.nav_drawer.set_state("close")
        self.parent.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        self.parent.parent.parent.parent.parent.parent.ids.edit_screen.edit_task(self)


class CustomNavigationDrawer(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload()

    def reload(self):
        self.clear_widgets()
        global TAG
        self.add_widget(MDNavigationDrawerHeader(title=TAG, padding=(0, 0, 0, 10)))  # source można dodać
        self.add_widget(MDNavigationDrawerDivider())
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="bell", on_release=self.print, text='bell'),
                                            text="Notifications", text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))
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
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="trash-can-outline", on_release=self.print, text='trash-can'),
                                            text='Trash', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="help-circle-outline", on_release=self.print, text='help'),
                                            text='Help', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))

    def print(self, butt):
        print(butt.text)

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
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        if butt.text == 'Labels':
            self.parent.parent.parent.ids.main_screen.update('category', 'category')
        else:
            self.parent.parent.parent.ids.main_screen.update('priority', int(butt.id))


class EditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_window = None
        self.remove_label_rowid = None

        self.touched_id = None
        self.absolute_pos_0 = None
        self.widget_y_0 = None
        self.labels = []

        self.widget_height = Window.size[0]*.1
        self.edit_window = RelativeLayout()

        self.save_button = MDFlatButton(text='SAVE', size_hint_x=.35, font_size=10,
                                     md_bg_color=(0, 0, 0, 0), theme_text_color="Custom", text_color=(1, 1, 1, 1))
        self.window = MDBoxLayout(
                    self.edit_window,
                    MDBoxLayout(
                        Label(size_hint_x=.3, color=(0, 0, 0, 0)),
                        MDFlatButton(text='CANCEL', size_hint_x=.35, font_size=10, on_release=self.exit,
                                     md_bg_color=(0, 0, 0, 0), theme_text_color="Custom", text_color=(1, 1, 1, .3)),
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
                                        MDTextField(id='text_field', text=label_name,
                                            text_color_focus='white', line_color_focus='white',
                                            required=True),
                                        MDIconButton(id=label_name, text=str(rowid), icon='trash-can-outline',
                                                     size_hint_x=.1, pos_hint={"center_x": .5, "center_y": .75},
                                                     on_release=self.remove_dialog),
                                        id=str(rowid), size_hint_y=None, height=self.widget_height))
        self.save_button.text = "SAVE"
        self.save_button.bind(on_release=self.save_label)

    def save_label(self, *args):
        if self.edit_window.children[0].ids['text_field'].text:
            database = sqlite3.connect('databases/to_do.db')
            db = database.cursor()

            db.execute("""
                            UPDATE Labels
                            SET label_name = {}
                            WHERE ROWID = {};
                        """.format('"'+self.edit_window.children[0].ids['text_field'].text+'"', self.edit_window.children[0].id))
            database.commit()
            database.close()

            self.parent.parent.ids.md_list_nav_drawer.reload()
            self.parent.parent.ids.main_screen.reload_labels(int(self.edit_window.children[0].id),
                                                            self.edit_window.children[0].ids['text_field'].text)
            self.exit()
            #self.save_button.unbind(on_release=self.save_label)
        else:
            if not self.info_window:
                self.info_window = Snackbar(text='Label name can not be empty!')
            self.info_window.open()
            Clock.schedule_once(self.close_info_window, 3)

    # add/remove label
    def add_label(self):
        self.window.height += self.widget_height
        self.edit_window.add_widget(MDTextField(id='text_field', text="", hint_text='Label Name:',
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
                                                                 self.edit_window.children[0].text)
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

        if self.parent.parent.ids.main_screen.which_label == self.remove_label_rowid:
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
                        MDTextField(id=str(item[1]), text=item[0], text_color_focus='white', line_color_focus='white', required=True),
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

        #  edit:
        #  1: zapisać do bd
        #  2: zamknąć EditScreen
        #  3: odświerzyć MainView

    def save_labels(self, *args):
        for label_tuple in self.labels:
            if not label_tuple[0].ids[str(label_tuple[1])].text:
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
                    """.format(len(self.labels)-idx, '"'+label_tuple[0].ids[str(label_tuple[1])].text+'"', label_tuple[1]))
            database.commit()
            self.parent.parent.ids.main_screen.reload_labels(int(label_tuple[1]),
                                                             label_tuple[0].ids[str(label_tuple[1])].text)
        database.close()

        self.labels = []
        self.parent.parent.ids.md_list_nav_drawer.reload()
        self.parent.parent.ids.main_screen.sort_labels()
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

        if task.notification:
            icon = 'bell'
            notification = task.notification
            notification_time = str(task.notification_time)
            not_disabled = False
            not_opacity = 1
        else:
            icon = 'bell-off-outline'
            notification = ""
            notification_time = ''
            not_disabled = True
            not_opacity = 0
        if task.deadline:
            deadline = task.deadline
        else:
            deadline = '-'

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
            MDTextField(
                text=task.note, line_color_focus=(1, 1, 1, 1), text_color_focus=(1, 1, 1, 1)),
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

    def show_date_picker(self, text):
        self.date_dialog = MDDatePicker(input_field_text_color_focus="white", helper_text=text,
             text_button_color="lightgrey",)
        self.date_dialog.bind(on_save=self.pick_data)
        self.date_dialog.open()

    def show_time_picker(self):
        self.date_dialog = MDTimePicker(input_field_text_color_focus="white",
             text_button_color="lightgrey",)
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
                            note = '{self.edit_window.children[0].children[2].text}',
                            eta = '{self.edit_window.children[0].children[1].children[1].text}',
                            notification = '{self.edit_window.children[0].children[3].children[2].text}',
                            notification_time = '{self.edit_window.children[0].children[3].children[1].text}'
                        WHERE ROWID = {rowid};
                    """)
        database.commit()
        database.close()

        self.parent.parent.ids.main_screen.reload_task(rowid)

        self.parent.parent.ids.main_screen.update()
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

        db.execute(f"""
                INSERT INTO Notes VALUES (
                                {label_id},
                                {self.edit_window.children[0].children[3].children[-2].text},
                                '{self.edit_window.children[0].children[0].children[0].text}',
                                '{self.edit_window.children[0].children[2].text}',
                                NULL,
                                0,
                                '{self.edit_window.children[0].children[1].children[1].text}',
                                '{self.edit_window.children[0].children[3].children[2].text}',
                                '{self.edit_window.children[0].children[3].children[1].text}');
                            """)
        database.commit()
        db.execute(f"""
                SELECT ROWID FROM Notes WHERE 
                            label_id = {label_id} AND
                            priority = {self.edit_window.children[0].children[3].children[-2].text} AND
                            deadline = '{self.edit_window.children[0].children[0].children[0].text}' AND
                            note = '{self.edit_window.children[0].children[2].text}' AND
                            eta = '{self.edit_window.children[0].children[1].children[1].text}' AND
                            notification = '{self.edit_window.children[0].children[3].children[2].text}' AND
                            notification_time = '{self.edit_window.children[0].children[3].children[1].text}'
                            """)
        rowid = int(db.fetchone()[0])
        database.close()

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
        self.save_button.unbind(on_release=self.save_tasks)
        self.save_button.unbind(on_release=self.save_labels)
        self.save_button.unbind(on_release=self.save_label)
        self.parent.current = 'screen'
        self.edit_window.clear_widgets()
        self.window.height = Window.size[0] * .15
        self.window.size_hint_x = .8


