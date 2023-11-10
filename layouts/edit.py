from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.graphics.texture import Texture

import cv2
import numpy as np
from datetime import date
from datetime import datetime
import sqlite3

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField

import include.get_from_db as get_from_db
import include.variables as global_variables
from layouts.labels import Task


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
        self.cancel_button = MDFlatButton(text='CANCEL', size_hint_x=.35, on_release=self.exit,
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

        if global_variables.which_label_global == self.remove_label_rowid:
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
                             size_hint_x=.2, text_color=global_variables.priority_colors[task.priority - 1],
                             theme_text_color='Custom', on_release=lambda x: self.priority_menu.open(),
                             pos_hint={"center_x": 0, "center_y": .6}, md_bg_color=(1, 1, 1, .03)),
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
        for number, color in enumerate(global_variables.priority_colors, 1):
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
        self.edit_window.children[0].children[-1].children[-2].text_color = global_variables.priority_colors[new_priority - 1]
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

        if global_variables.which_label_global != 'calendar':
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
            if global_variables.which_label_global == 'calendar':
                self.parent.current = 'calendar'
            else:
                self.parent.current = 'screen'