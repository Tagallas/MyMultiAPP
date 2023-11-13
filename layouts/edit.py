from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

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
from include.function import ndarray_to_texture


class EditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # attributes
        self.info_window = None
        self.images_list = None
        self.new_task = None
        self.label_id = None
        self.label_name = None
        self.task = None

        self.widget_height = Window.size[0]*.1

        # creating main window
        self.edit_window = RelativeLayout(size_hint_y=None)

        # creating save and cancel button
        self.save_button = MDFlatButton(text='SAVE', size_hint_x=.35,
                                        md_bg_color=(0, 0, 0, 0), theme_text_color="Custom", text_color=(1, 1, 1, 1))
        self.cancel_button = MDFlatButton(text='CANCEL', size_hint_x=.35, on_release=self.exit,
                                          md_bg_color=(0, 0, 0, 0), theme_text_color="Custom", text_color=(1, 1, 1, .3))

        # creating whole window
        self.window = MDBoxLayout(
                    self.edit_window,
                    MDBoxLayout(
                        Label(size_hint_x=.3, color=(0, 0, 0, 0)),
                        self.cancel_button,
                        self.save_button,
                        size_hint_y=None, height=Window.size[0] * .07),
                    size_hint=(.8, None), height=Window.size[0] * .15, md_bg_color=(.15, .15, .15, 1),
                    pos_hint={"center_x": .5, "center_y": .5}, orientation='vertical',
                    spacing=self.widget_height*.1, padding=(self.widget_height*.3, 0, self.widget_height*.3, 0))
        self.add_widget(self.window)

    # edit label
    def build_label(self, rowid, label_name):
        # increasing window size
        self.window.height += self.widget_height
        # creating and displaying Edit label screen
        self.edit_window.add_widget(EditLabel(self, rowid, label_name, id=str(rowid), size_hint_y=None,
                                              height=self.widget_height))

        # if adding label
        if rowid == -1:
            self.save_button.text = "ADD"
            self.save_button.bind(on_release=self.edit_window.children[0].add)
        # if editing label
        else:
            self.save_button.text = "SAVE"
            self.save_button.bind(on_release=self.edit_window.children[0].save)

    # save label after editing
    def save_label(self, rowid, label_name):
        # updating navigation drawer
        self.parent.parent.ids.md_list_nav_drawer.reload()
        # updating edited label in main screen
        self.parent.parent.ids.main_screen.reload_labels(rowid, label_name)

        # calling function to exit edit screen
        self.exit()

    # add new label
    def add_label(self, rowid, label_name, priority):
        # updating navigation drawer
        self.parent.parent.ids.md_list_nav_drawer.reload()
        # updating edited label in main screen
        self.parent.parent.ids.main_screen.reload_labels(rowid, label_name, priority)

        # unbinding save button
        self.save_button.unbind(on_release=self.edit_window.children[0].add)

        # calling function to exit edit screen
        self.exit()

    # edit all labels
    def build_labels(self):
        # creating and displaying Edit label screen
        self.edit_window.add_widget(EditLabels(self, self.widget_height))

        # editing button parameters
        self.save_button.text = "SAVE"
        self.save_button.bind(on_release=self.edit_window.children[0].save)

    # save all labels
    def save_labels(self):
        # updating navigation drawer
        self.parent.parent.ids.md_list_nav_drawer.reload()
        # updating main screen
        self.parent.parent.ids.main_screen.update('category', 'category', 'asc')

        # calling function to exit edit screen
        self.exit()

    # remove label dialog
    def remove_dialog(self, rowid, text):
        # creating dialog
        self.info_window = MDDialog(
            text="Remove label: " + text + '?',
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
                    on_release=lambda x: {self.close_info_window(),
                                          self.remove_label(rowid)}
                ), ], )

        # displaying dialog
        self.info_window.open()

    # permanently remove label
    def remove_label(self, rowid, *args):
        # closing info window
        self.close_info_window()
        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # deleting label and tasks from label
        db.execute(" DELETE FROM Labels WHERE ROWID = " + str(rowid))
        db.execute(" DELETE FROM Notes WHERE label_id = " + str(rowid))
        database.commit()
        database.close()

        # deleting label from main screen
        self.parent.parent.ids.main_screen.remove_label(int(rowid))

        # if sorted by removed label
        if global_variables.which_label_global == self.remove_label_rowid:
            # sort by category
            self.parent.parent.ids.main_screen.update('category', 'category')

        # updating navigation drawer
        self.parent.parent.ids.md_list_nav_drawer.reload()

        # if editing all labels
        if isinstance(self.edit_window.children[0], EditLabels):
            # clearing widgets and editing all labels once again
            self.save_button.unbind(on_release=self.edit_window.children[0].save)
            self.edit_window.clear_widgets()
            self.window.height = Window.size[0] * .15
            self.build_labels()

        # if editing one label
        else:
            # unbinding button
            self.save_button.unbind(on_release=self.edit_window.children[0].save)
            # exiting Edit Screen
            self.exit()

        #

    # edit task
    def build_task(self, task):
        # changing window size
        self.window.height += self.widget_height * 4
        self.window.size_hint_x = .9

        # editing task
        self.edit_window.add_widget(EditTask(self, task, self.widget_height, height=self.widget_height * 4.5))

        # changing button parameters
        self.save_button.text = "SAVE"
        self.save_button.bind(on_release=self.edit_window.children[0].save)

    def add_task(self, label_id, label_name):
        # creating new task widget
        self.new_task = Task(label_name, label_id, 0, 1, '', '', '-', date.today().strftime('20%y-%m-%d'), '', -1)

        # editing new task
        self.build_task(self.new_task)

    # adding all task images
    def add_img_tasks(self, images_list=None, label_id=None, label_name=None):
        # when calling function first time
        if images_list:
            # updating image list, label id and label name
            self.images_list = images_list
            self.label_id = label_id
            self.label_name = label_name

        # if any images left
        if self.images_list:
            # creating new task
            self.task = Task(self.label_name, self.label_id, 0, 1, self.images_list[0], '', '-',
                             date.today().strftime('20%y-%m-%d'), '', -1)
            # deleting last image
            del self.images_list[0]
            # editing new task
            self.build_task(self.task)

        # if no images left
        else:
            self.exit()

    # save task
    def save_task(self, rowid):
        # if not calendar view
        if global_variables.which_label_global != 'calendar':
            # updating main screen
            self.parent.parent.ids.main_screen.update()
        # if calendar view
        else:
            # updating calendar view task
            self.parent.parent.ids.calendar_view.reload_task(rowid)

        # reloading task
        self.parent.parent.ids.main_screen.reload_task(rowid)

        # exiting edit screen
        self.exit()

    # add task
    def save_new_task(self, task):
        # adding task widget
        self.parent.parent.ids.main_screen.add_task(task)
        # reloading task
        self.parent.parent.ids.main_screen.reload_task(task.rowid)

        # unbinding save button
        self.save_button.unbind(on_release=self.edit_window.children[0].save)

        # exiting edit screen
        self.exit()

    def close_info_window(self, *args):
        # if info window exists
        if self.info_window:
            # clearing widget
            self.info_window.dismiss()
            self.info_window = None

    def snackbar_open(self, text):
        # checking if info window exists
        if not self.info_window:
            # creating widget
            self.info_window = Snackbar(text=text)
        # displaying
        self.info_window.open()

        # closing info window after 3s
        Clock.schedule_once(self.close_info_window, 3)

    # leaving edit screen
    def exit(self, *args):
        # unbinding save button
        self.save_button.unbind(on_release=self.edit_window.children[0].save)

        # clearing widgets
        self.edit_window.clear_widgets()
        self.window.height = Window.size[0] * .15
        self.window.size_hint_x = .8

        # if adding image tasks
        if self.images_list:
            self.add_img_tasks()
        # if exiting edit screen
        else:
            # if previously in calendar view
            if global_variables.which_label_global == 'calendar':
                self.parent.current = 'calendar'
            # if previously in screen view
            else:
                self.parent.current = 'screen'


class EditLabel(MDBoxLayout):
    def __init__(self, parent, rowid, label_name, **kwargs):
        super().__init__(**kwargs)
        # attributes
        self.rowid = rowid
        self.edit_screen = parent

        # creating widgets
        self.dialog = None
        self.text_field = MDTextField(text=label_name, text_color_focus='white', line_color_focus='white',
                                      required=True)
        self.add_widget(self.text_field)

        # if editing label
        if rowid != -1:
            self.remove_icon = MDIconButton(icon='trash-can-outline', size_hint_x=.1,
                                            pos_hint={"center_x": .5, "center_y": .75}, on_release=self.remove_dialog)
            self.add_widget(self.remove_icon)

    def save(self, *args):
        # if label name is not empty
        if self.text_field.text:
            # connecting to database
            database = sqlite3.connect('databases/to_do.db')
            db = database.cursor()

            # updating label
            db.execute("""
                            UPDATE Labels
                            SET label_name = {}
                            WHERE ROWID = {};
                        """.format('"'+self.text_field.text+'"', self.rowid))
            database.commit()
            database.close()

            # calling save function in Edit Screen
            self.edit_screen.save_label(self.rowid, self.text_field.text)

        # if label name is empty
        else:
            # calling function from Edit Screen to inform about invalid data
            self.edit_screen.snackbar_open('Label name can no be empty!')

    def add(self, *args):
        # if label name is not empty
        if self.text_field.text:
            # connecting to database
            database = sqlite3.connect('databases/to_do.db')
            db = database.cursor()

            # getting number of existing labels
            db.execute(""" SELECT COUNT(ROWID) FROM Labels """)
            number_of_labels = db.fetchone()

            # adding new label
            db.execute(" INSERT INTO Labels VALUES (" + str(number_of_labels[0]+2) + ", '" +
                       self.text_field.text + "'); ")
            database.commit()

            # getting new rowid
            db.execute(f"SELECT ROWID from Labels WHERE label_name = '{self.text_field.text}'")
            rowid = db.fetchone()[0]
            database.close()

            # calling add function in Edit Screen
            self.edit_screen.add_label(rowid, self.text_field.text, str(number_of_labels[0]+2))

        # if label name is empty
        else:
            # calling function from Edit Screen to inform about invalid data
            self.edit_screen.snackbar_open('Label name can no be empty!')

    def remove_dialog(self, *args):
        # calling function from Edit Screen to display conformation about removing label
        self.edit_screen.remove_dialog(self.rowid, self.text_field.text)


class EditLabels(RelativeLayout):
    def __init__(self, parent, label_height, **kwargs):
        super().__init__(**kwargs)
        # parameters
        self.size_hint_y = None
        self.height = 0
        self.edit_screen = parent

        # attributes
        self.label_height = label_height

        self.touched_id = None
        self.widget_y_0 = None
        self.absolute_pos_0 = None

        self.labels = []
        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name, ROWID FROM Labels ORDER BY priority DESC")
        items = db.fetchall()
        database.close()

        # for every label
        for idx, item in enumerate(items):
            # creating and displaying label
            self.labels.append((MDBoxLayout(
                MDIconButton(icon='dots-horizontal', size_hint_x=None, width=self.height * 1.5, text=str(item[1]),
                             pos_hint={"center_x": .5, "center_y": .8}, ripple_alpha=0, on_press=self.dots_press,
                             id='icon_but'),
                MDTextField(text=item[0], text_color_focus='white', line_color_focus='white', required=True),
                MDIconButton(id=item[0], text=str(item[1]), icon='trash-can-outline',
                             size_hint_x=.1, pos_hint={"center_x": .5, "center_y": .75},
                             on_release=self.remove_dialog, icon_size=self.label_height * .5),
                size_hint_y=None, height=self.label_height, orientation='horizontal', pos=(0, self.height),
                spacing=self.label_height * .1), item[1]))

            # increasing window height
            self.height += self.label_height

            # displaying label
            self.add_widget(self.labels[-1][0])

        # increasing window from Edit Screen size
        self.edit_screen.window.height = self.height + self.label_height * 1.5

    def save(self, *args):
        # for every label
        for label_tuple in self.labels:
            # checking if label name is not empty
            if not label_tuple[0].children[1].text:
                # displaying snackbar
                self.edit_screen.snackbar_open('Label name can not be empty!')
                return

        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # for every label
        for idx, label_tuple in enumerate(self.labels, 1):
            # updating label data
            db.execute("""
                        UPDATE Labels
                        SET priority = {}, label_name = {}
                        WHERE ROWID = {};
                    """.format(len(self.labels) - idx, '"' + label_tuple[0].children[1].text + '"', label_tuple[1]))
            database.commit()

            # updating label
            self.edit_screen.parent.parent.ids.main_screen.reload_labels(int(label_tuple[1]),
                                                                         label_tuple[0].children[1].text)
        database.close()

        # clearing labels list
        self.labels = []
        # calling save function in Edit Screen
        self.parent.parent.parent.save_labels()

    def remove_dialog(self, butt):
        # calling function from Edit Screen to display conformation about removing label
        self.parent.parent.parent.remove_dialog(int(butt.text), str(butt.id))

    def dots_press(self, but):
        # looking for label
        for label_id in range(len(self.labels)):
            if self.labels[label_id][0].ids[str('icon_but')].text == but.text:
                # saving touched label id and position
                self.touched_id = label_id
                self.widget_y_0 = but.parent.pos[1]
                return
        # if some errors
        raise Exception("Didn't find label with text: {}".format(but.text))

    def on_touch_move(self, touch):
        # if we touched label
        if self.touched_id is not None:
            # if no absolute position (we have not moved label yet)
            if self.absolute_pos_0 is None:
                # absolute position = out touched position
                self.absolute_pos_0 = touch.y
            # if absolute position (we move label)
            else:
                # actual relative position
                pos_relative = touch.y - self.absolute_pos_0 + self.widget_y_0

                # if touched position in our window
                if 0 < pos_relative < self.label_height * (len(self.labels) - 1):
                    # if we moved over another label
                    if self.touched_id < len(self.labels) and pos_relative > self.widget_y_0 + self.label_height*.75:
                        # moving another label under touched label
                        self.labels[self.touched_id+1][0].pos[1] -= self.label_height
                        # changing both labels id
                        self.labels[self.touched_id], self.labels[self.touched_id+1] = \
                            self.labels[self.touched_id+1], self.labels[self.touched_id]
                        self.touched_id += 1
                        # updating label relative and absolute y0
                        self.widget_y_0 += self.label_height
                        self.absolute_pos_0 += self.label_height

                    # if we moved under another label
                    elif self.touched_id > 0 and pos_relative < self.widget_y_0 - self.label_height*.75:
                        # moving another label over touched label
                        self.labels[self.touched_id - 1][0].pos[1] += self.label_height
                        # changing both labels id
                        self.labels[self.touched_id], self.labels[self.touched_id - 1] = \
                            self.labels[self.touched_id - 1], self.labels[self.touched_id]
                        self.touched_id -= 1
                        # updating label relative and absolute y0
                        self.widget_y_0 -= self.label_height
                        self.absolute_pos_0 -= self.label_height

                    # updating label position
                    self.labels[self.touched_id][0].y = pos_relative

                # if touched position under our window
                elif pos_relative < 0:
                    # label position at the bottom of our window
                    self.labels[self.touched_id][0].y = 0

                # if touched position over our window
                else:
                    # label position at the top of our window
                    self.labels[self.touched_id][0].y = self.label_height * (len(self.labels) - 1)

    def on_touch_up(self, touch):
        # if we touched label
        if self.touched_id is not None:
            # centering touched label
            self.labels[self.touched_id][0].pos[1] = self.widget_y_0

            # clearing data
            self.touched_id = None
            self.absolute_pos_0 = None


class EditTask(MDBoxLayout):
    def __init__(self, parent, task, w_height, **kwargs):
        super().__init__(**kwargs)
        # parameters
        self.orientation = 'vertical'
        self.size_hint_y = None

        # attributes
        self.edit_screen = parent
        self.task = task
        self.widget_height = w_height
        self.priority_menu = None
        self.label_name_menu = None
        self.notification_menu = None
        self.date_dialog = None

        # building widget
        self.build()

    def save(self, *args):
        # getting rowid
        rowid = int(self.children[0].children[0].id)
        # if adding task
        if rowid == -1:
            self.add()
            return

        # getting label id
        label_id = int(self.children[1].children[-1].id)

        # checking every letter in eta
        for el in self.children[1].children[1].text:
            # if letter between 0 and 9
            if el < str(0) or el > str(9):
                # if letter other than "-"
                if self.children[1].children[1].text != '-':
                    self.edit_screen.snackbar_open('ETA incorrect! Set to NULL')
                    # setting eta to "-"
                    self.children[1].children[1].text = '-'

        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # updating task
        db.execute(f"""
                                UPDATE Notes
                                SET label_id = {label_id},
                                    priority = {self.children[3].children[-2].text},
                                    deadline = '{self.children[0].children[0].text}',
                                    eta = '{self.children[1].children[1].text}',
                                    notification = '{self.children[3].children[2].text}',
                                    notification_time = '{self.children[3].children[1].text}'
                                WHERE ROWID = {rowid};
                            """)

        # if note is text
        if isinstance(self.children[2], MDTextField):
            # updating task note
            db.execute(f"""
                                    UPDATE Notes
                                    SET note = '{self.children[2].text}'
                                    WHERE ROWID = {rowid};
                                """)
        database.commit()
        database.close()

        # calling function to update task
        self.edit_screen.save_task(rowid)

    def add(self, *args):
        # getting label id
        label_id = int(self.children[1].children[-1].id)

        # for every letter in eta
        for el in self.children[1].children[1].text:
            # if letter between 0 and 9
            if el < str(0) or el > str(9):
                # if letter other than "-"
                if self.children[1].children[1].text != '-':
                    self.edit_screen.snackbar_open('ETA incorrect! Set to NULL')
                    # setting eta to "-"
                    self.children[1].children[1].text = '-'

        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        note = ''
        img = None
        shape = None
        # if note is text
        if isinstance(self.children[2], MDTextField):
            note = self.children[2].text
        # if note is image
        else:
            img = sqlite3.Binary(self.task.note)
            shape = np.array(img.shape)

        # adding new task
        db.execute("""
                        INSERT INTO Notes (label_id, priority, deadline, note, image, active, eta, notification,
                        notification_time, shape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (label_id, self.children[3].children[-2].text,
                              self.children[0].children[0].children[0].text, note, img, 0,
                              self.children[1].children[1].text,
                              self.children[3].children[2].text,
                              self.children[3].children[1].text, shape))

        database.commit()

        # getting rowid
        db.execute("""SELECT ROWID, note FROM Notes ORDER BY ROWID DESC """)
        rowid = int(db.fetchone()[0])

        # setting new rowid
        self.task.rowid = rowid

        # calling function from Edit Screen to add task widget
        self.edit_screen.save_new_task(self.task)

        # clearing data
        self.task = None

    def build(self):
        task = self.task

        # getting proper eta format
        if task.eta:
            eta = task.eta
        else:
            eta = "-"

        # getting proper notification format
        # no notification
        if task.calendar == 0:
            icon = 'bell-off-outline'
            notification = ""
            notification_time = ''
            not_disabled = True
            not_opacity = 0
        # no notification, but saved in calendar
        elif task.calendar == 1:
            icon = 'calendar'
            notification = task.notification
            notification_time = str(task.notification_time)
            not_disabled = False
            not_opacity = 1
        # notification and saved in calendar
        else:
            icon = 'bell'
            notification = task.notification
            notification_time = str(task.notification_time)
            not_disabled = False
            not_opacity = 1

        # getting proper deadline format
        if task.deadline:
            deadline = task.deadline
        else:
            deadline = '-'

        # getting proper note format
        note_widget = None
        # if note is a text
        if isinstance(task.note, str):
            note_widget = MDTextField(
                text=task.note, line_color_focus=(1, 1, 1, 1), text_color_focus=(1, 1, 1, 1))
        # if note is an image
        else:
            image_texture = ndarray_to_texture(task.note, 'luminance')
            note_widget = Image(texture=image_texture, pos_hint={'center_x': .5, 'center_y': .5},
                                size_hint_y=None, height=self.widget_height*1.5)

        # adding first row (priority, notification time and date)
        self.add_widget(MDBoxLayout(
                Label(size_hint_x=.2, text='priority:'),
                MDIconButton(id='priority', text=str(task.priority), icon=f'numeric-{task.priority}-box-outline',
                             size_hint_x=.2, text_color=global_variables.priority_colors[task.priority - 1],
                             theme_text_color='Custom', on_release=lambda x: self.priority_menu.open(),
                             pos_hint={"center_x": 0, "center_y": .6}, md_bg_color=(1, 1, 1, .03)),
                Label(size_hint_x=.01),
                MDFlatButton(id='date', size_hint_x=.3, text=notification, pos_hint={"center_x": 0, "center_y": .6},
                             disabled=not_disabled, font_size=self.widget_height*.35, md_bg_color=(1, 1, 1, .03),
                             opacity=not_opacity, on_release=lambda x: self.show_date_picker('notification')),
                MDFlatButton(id='time', size_hint_x=.1, text=notification_time,
                             pos_hint={"center_x": 0, "center_y": .6},
                             disabled=not_disabled, font_size=self.widget_height*.35, md_bg_color=(1, 1, 1, .03),
                             opacity=not_opacity, on_release=lambda x: self.show_time_picker()),
                MDIconButton(text='notification', size_hint_x=.1, pos_hint={"center_x": 0, "center_y": .6},
                             md_bg_color=(1, 1, 1, .03), on_release=lambda x: self.notification_menu.open(),
                             icon=f"{icon}", icon_size=self.widget_height*.5),
                size_hint_y=None, height=self.widget_height*.7, orientation='horizontal'),)

        # adding note
        self.add_widget(note_widget)

        # adding 3rd row (label name, eta)
        self.add_widget(MDBoxLayout(
                MDFlatButton(id=f"{task.label_id}", text=task.label_name, size_hint_x=.4,
                             on_release=lambda x: self.label_name_menu.open(), md_bg_color=(1, 1, 1, .03)),
                Label(size_hint_x=.25),
                Label(text='eta: ', size_hint_x=.1, pos_hint={"center_x": 0, "center_y": .75}),
                TextInput(text=f"{eta}", size_hint=(.2, None), background_color=(1, 1, 1, .03),
                          foreground_color=(1, 1, 1, 1), multiline=False, font_size=self.widget_height*.4,
                          height=self.widget_height, cursor_color=(1, 1, 1, 1),
                          pos_hint={"center_x": 0, "center_y": .6}),
                Label(text='min', size_hint_x=.1, pos_hint={"center_x": 0, "center_y": .75}),
                size_hint_y=None, height=self.widget_height*.7, orientation='horizontal', ),)

        # adding 4th row(active, deadline)
        self.add_widget(MDBoxLayout(
                Label(text='active: ', size_hint_x=.2),
                CheckBox(size_hint_x=.1, active=task.check_box.active, pos_hint={"center_x": 1, "center_y": .45},
                         disabled=True),
                Label(size_hint_x=.2),
                Label(size_hint_x=.2, text='deadline:', pos_hint={"center_x": 0, "center_y": .5}),
                MDFlatButton(size_hint_x=.4, text=deadline, pos_hint={"center_x": 0, "center_y": .5},
                             font_size=self.widget_height * .35, md_bg_color=(1, 1, 1, .03),
                             on_release=lambda x: self.show_date_picker('deadline'), id=str(task.rowid)),
                size_hint_y=None, height=self.widget_height, orientation='horizontal'),)

        # priority icon list
        priority_items = []
        # for every priority
        for number, color in enumerate(global_variables.priority_colors, 1):
            # adding new priority item
            priority_items.append({
                "viewclass": "MDIconButton",
                "icon": f'numeric-{str(number)}-box-outline',
                "icon_size": self.widget_height*.7,
                "text_color": color,
                "theme_text_color": 'Custom',
                "on_release": lambda x=number: self.update_priority(x)
            })
        # creating priority dropdown menu
        self.priority_menu = MDDropdownMenu(caller=self.children[-1].children[-2],
                                            items=priority_items, max_height=self.widget_height*5.8)

        # label name list
        label_name_items = []
        tuple_ln_rowid = get_from_db.get_label_names('to_do')
        # for every label
        for label_name, rowid in tuple_ln_rowid:
            # adding new label item
            label_name_items.append({
                "viewclass": "MDFlatButton",
                "text": f"{label_name}",
                "on_release": lambda x=label_name, y=rowid: self.update_label_name(x, y)
            })
        # creating label name dropdown menu
        self.label_name_menu = MDDropdownMenu(caller=self.children[-3].children[-1],
                                              items=label_name_items, width_mult=2,
                                              max_height=min(self.widget_height*5.8,
                                                             self.widget_height*1.1*len(tuple_ln_rowid)),)

        # notification list
        notification_items = []
        for icon in ['bell-off-outline', 'bell']:
            # adding notification item
            notification_items.append({
                "viewclass": "MDIconButton",
                "icon": icon,
                "text_color": (1, 1, 1, 1),
                "icon_size": self.widget_height * .5,
                "on_release": lambda x=icon, y=task: self.update_notification(x, y)
            })
        # creating notification dropdown menu
        self.notification_menu = MDDropdownMenu(caller=self.children[-1].children[0],
                                                width_mult=.5, items=notification_items,
                                                max_height=self.widget_height*2.8, position='center')

    def show_date_picker(self, text):
        # creating and binding date picker
        self.date_dialog = MDDatePicker(helper_text=text, text_button_color="lightgrey", )
        self.date_dialog.bind(on_save=self.pick_data)

        # displaying date picker
        self.date_dialog.open()

    def show_time_picker(self):
        # creating and binding time picker
        self.date_dialog = MDTimePicker(text_button_color="lightgrey", )
        self.date_dialog.bind(on_save=self.pick_time)
        # setting current time
        self.date_dialog.set_time(datetime.now())

        # displaying time picker
        self.date_dialog.open()

    # called when saving new time
    def pick_time(self, instance, value, *args):
        self.children[-1].children[1].text = value.strftime("%H:%M")

    # called when saving new data
    def pick_data(self, instance, value, *args):
        # if correct data
        if str(value) >= date.today().strftime("20%y-%m-%d"):
            # if changing notification data
            if self.date_dialog.helper_text == 'notification':
                self.children[-1].children[2].text = str(value)
            # if changing deadline data
            elif self.date_dialog.helper_text == 'deadline':
                self.children[0].children[0].text = str(value)
        # if incorrect data
        else:
            self.edit_screen.snackbar_open('Date can not be earlier than today!')
            return

    # called when updating task priority
    def update_priority(self, new_priority):
        # updating priority icon
        self.children[-1].children[-2].icon = f'numeric-{new_priority}-box-outline'
        # updating priority number
        self.children[-1].children[-2].text = str(new_priority)
        # updating priority color
        self.children[-1].children[-2].text_color = global_variables.priority_colors[new_priority - 1]

        # closing priority dropdown menu
        self.priority_menu.dismiss()

    # called when changing label name
    def update_label_name(self, label_name, rowid):
        # updating label name
        self.children[-3].children[-1].text = label_name
        # updating rowid
        self.children[-3].children[-1].id = f"{rowid}"

        # closing label dropdown menu
        self.label_name_menu.dismiss()

    # called when updating notification icon
    def update_notification(self, icon, task):
        # closing notification menu
        self.notification_menu.dismiss()

        # if updated to notification
        if icon == 'bell':
            # if previous set notification
            if task.notification:
                # updating notification time and date
                notification = task.notification
                time = task.notification_time
            # if no notification set
            else:
                # setting current time and date
                notification = date.today().strftime("20%y-%m-%d")
                time = datetime.now().strftime("%H:%M")

            # updating notification date and widget properties
            self.children[-1].children[2].text = notification
            self.children[-1].children[2].disabled = False
            self.children[-1].children[2].opacity = 1

            # updating notification time and widget properties
            self.children[-1].children[1].text = time
            self.children[-1].children[1].disabled = False
            self.children[-1].children[1].opacity = 1

            # updating notification icon
            self.children[-1].children[0].icon = 'bell'

        # if updated to delete notification
        else:
            # updating notification date and widget properties
            self.children[-1].children[2].text = ""
            self.children[-1].children[2].disabled = True
            self.children[-1].children[2].opacity = 0

            # updating notification time and widget properties
            self.children[-1].children[1].text = ""
            self.children[-1].children[1].disabled = True
            self.children[-1].children[1].opacity = 0

            # updating notification icon
            self.children[-1].children[0].icon = 'bell-off-outline'
