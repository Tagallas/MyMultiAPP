from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image

import numpy as np
from datetime import date
import sqlite3

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDIcon

from include.function import ndarray_to_texture, sort
import include.variables as global_variables


class MainView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # dictionary with labels {rowid: class<LabelLayout()>
        self.labels = {}
        # list with tasks [class<Task>]
        self.tasks = []

        # retrieving labels from database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT ROWID, label_name, priority FROM Labels ORDER BY priority")
        labels = db.fetchall()

        # getting tasks
        for label in labels:
            # label = [Rowid, label_name, priority]
            self.labels[label[0]] = LabelLayout(label[0], label[1], label[2])
            self.add_widget(self.labels[label[0]])

            # retrieving tasks from database
            db.execute("""SELECT N.active, N.priority, N.note, N.notification, N.eta, N.deadline, N.notification_time,
                        N.ROWID, N.image, N.shape
            FROM Labels AS L LEFT JOIN Notes AS N ON L.ROWID = N.label_id
            WHERE N.label_id = {} ORDER BY N.active, N.priority, N.deadline""".format(label[0]))
            items = db.fetchall()

            # for every task
            for i in items:
                # creating a class object with note as text
                if i[9] is None:
                    self.tasks.append(Task(label[1], str(label[0]), i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
                # creating a class object with note as image
                else:
                    shape = np.frombuffer(i[9], dtype='int32')  # shape -> array[height, width]
                    img = np.frombuffer(i[8], dtype=np.uint8)  # img -> array[n, 1]
                    img.shape = shape
                    self.tasks.append(Task(label[1], str(label[0]), i[0], i[1], img, i[3], i[4], i[5], i[6], i[7]))

                self.labels[label[0]].add_task(self.tasks[-1])

        database.close()

    def add_task(self, task):
        self.tasks.append(task)

    # reloads task after editing
    def reload_task(self, rowid):
        # looking for a specific task
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:

                prev_label_id = int(self.tasks[i].label_id)

                database = sqlite3.connect('databases/to_do.db')
                db = database.cursor()
                db.execute(f"""SELECT active, priority, note, notification, eta, deadline, notification_time,
                        ROWID, label_id, image, shape FROM Notes WHERE ROWID = {rowid}""")
                task_atr = db.fetchone()

                db.execute(f"""SELECT label_name FROM Labels WHERE ROWID = {task_atr[8]}""")
                label_name = db.fetchone()

                # creating a class object with note as text
                if task_atr[10] is None:
                    self.tasks[i] = Task(label_name[0], task_atr[8], task_atr[0], task_atr[1], task_atr[2], task_atr[3],
                                         task_atr[4], task_atr[5], task_atr[6], task_atr[7])
                # creating a class object with note as image
                else:
                    shape = np.frombuffer(task_atr[10], dtype='int32')  # shape -> array[height, width]
                    img = np.frombuffer(task_atr[9], dtype=np.uint8)  # img -> array[n, 1]
                    img.shape = shape
                    self.tasks[i] = Task(label_name[0], task_atr[8], task_atr[0], task_atr[1], img, task_atr[3],
                                         task_atr[4], task_atr[5], task_atr[6], task_atr[7])

                # when label name was changed
                if int(prev_label_id) != task_atr[8]:
                    # removing task from previous label
                    self.labels[prev_label_id].remove_task(rowid)

                # when label name was not changed
                else:
                    # removing task from current label (to reload it)
                    self.labels[task_atr[8]].remove_task(rowid)
                # adding task to new label
                self.labels[task_atr[8]].add_task(self.tasks[i])

                # sorting tasks if necessary
                if global_variables.which_label_global not in ('all', 'calendar'):
                    self.labels[task_atr[8]].sort_label_layout()

                database.close()
                return

    # called when deactivating task
    def disable_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                task = self.tasks[i]
                task.opacity = .3
                # transports task to the bottom
                self.remove_widget(task)
                self.add_widget(task)
                return

    # called when task is again active
    def activate_task(self, rowid):
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                task = self.tasks[i]
                task.opacity = 1
                # updating layout to sort tasks
                self.update()
                return

    # called after editing or adding label
    def reload_labels(self, rowid, label_name, priority=None):
        # after editing
        if rowid in self.labels.keys():
            self.labels[rowid].reload_label()
            # sort tasks
            self.update(None, int(rowid))
        # after adding
        else:
            # create and add class<LabelLayout>
            self.labels[rowid] = LabelLayout(rowid, label_name, priority)
            # sort tasks
            self.update('priority', int(rowid), 'asc')

    # called when removing label
    def remove_label(self, rowid):
        # deleting every task
        for task in self.tasks:
            if task.label_id == rowid:
                self.tasks.remove(task)
        # deleting label
        self.remove_widget(self.labels[rowid])
        del self.labels[rowid]

    # sorting tasks
    def update(self, order_by=None, which_label=None, asc=None):
        self.clear_widgets()

        # reading from previous sort setting if necessary
        if order_by is None:
            order_by = global_variables.order_by_global
        if which_label is None:
            which_label = global_variables.which_label_global
        if asc is None:
            asc = global_variables.asc_global

        # saving sort settings
        global_variables.order_by_global = order_by
        global_variables.asc_global = asc
        global_variables.which_label_global = which_label

        # sorting by priority asc when all labels are visible
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
            # sorting by priority asc when all labels are visible
            if which_label == 'category':
                which_label = 'all'
                global_variables.which_label_global = which_label

            # sorting when all tasks are visible
            if which_label == 'all':
                for key in self.labels.keys():
                    # hiding tasks grouped by category
                    self.labels[key].hide_tasks()

                # sorting all tasks
                sort(self.tasks, asc)

                disabled = []
                for task in self.tasks:
                    # displaying task if is not completed
                    if not task.active:
                        self.add_widget(task)
                    # adding task do disabled list if is completed
                    else:
                        disabled.append(task)

                # displaying all completed tasks (at the bottom)
                for task in disabled:
                    self.add_widget(task)

            # sorting one label
            else:
                self.labels[which_label].sort_label_layout(order_by, asc)
                # displaying that label
                self.add_widget(self.labels[which_label])


class LabelLayout(MDBoxLayout):
    def __init__(self, rowid, label_name, priority, **kwargs):
        super().__init__(**kwargs)
        # parameters
        self.orientation = 'vertical'
        self.size_hint_y = None

        # attributes
        self.priority = priority
        self.rowid = rowid
        self.tasks = []
        self.disabled_tasks = []

        # task height
        self.widget_height = Window.size[1] / 13
        # whole layout height
        self.height = self.widget_height * 1.65

        self.label = TaskLabel(label_name)
        self.add_widget(self.label)

        # widget that adds new task or creates new photo
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

    # disable task = mark completed and move to the bottom
    def disable_task(self, rowid):
        # looking for task
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                # creating copy
                task = self.tasks[i]
                size = len(self.tasks) + len(self.disabled_tasks)

                # deleting task
                del self.tasks[i]

                # displaying task as completed
                self.disabled_tasks.append(task)
                task.opacity = .3

                # for every task
                for j in range(i, len(self.tasks)):
                    # move disabled task to the bottom
                    self.children[size-j-1], self.children[size-j] = self.children[size-j], self.children[size-j-1]
                return

    # activating completed task
    def activate_task(self, rowid):
        # looking for task
        for i in range(len(self.disabled_tasks)):
            if self.disabled_tasks[i].rowid == rowid:
                # removing from disabled
                task = self.disabled_tasks[i]
                del self.disabled_tasks[i]

                # adding to not completed
                self.tasks.append(task)
                task.opacity = 1

                # sorting label layout
                self.sort_label_layout()
                return

    # editing task
    def add_window(self):
        # changing screen to edit
        self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        # giving parameters of label
        self.parent.parent.parent.parent.parent.ids.edit_screen.add_task(self.rowid, self.label.label_name)

    def remove_task(self, rowid):
        # looking for task
        for i in range(len(self.tasks)):
            if self.tasks[i].rowid == rowid:
                # if tasks are sorted by labels
                if global_variables.which_label_global != 'all':
                    # no longer display task
                    self.remove_widget(self.tasks[i])
                self.height -= self.widget_height

                # delete task from label
                del self.tasks[i]
                return

    def remove_disabled(self):
        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # for every disabled task
        for task in self.disabled_tasks:
            # remove from label
            self.height -= self.widget_height
            self.remove_widget(task)

            # auxiliary variables
            note = ''
            img = None
            shape = None
            # if note is string
            if isinstance(task.note, str):
                note = task.note
            # if note is photo
            else:
                img = sqlite3.Binary(task.note)
                shape = np.array(task.note.shape)

            # insert task to deleted tasks
            db.execute("""
                    INSERT INTO Trash (label_id, priority, deadline, note, image, eta, notification, 
                    notification_time, deleted_date, shape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (task.label_id, task.priority, task.deadline, note, img, task.eta, task.notification,
                          task.notification_time, str(date.today().strftime("20%y-%m-%d")), shape))
            database.commit()

            # remove task from tasks
            db.execute(f"""
                            DELETE FROM Notes
                            WHERE ROWID = {task.rowid};
                        """)
            database.commit()

        # empty disabled tasks list for this label
        self.disabled_tasks = []
        database.close()

    def sort_label_layout(self, order_by=None, asc=None):
        # read from previous sort setting if necessary
        if order_by is not None:
            global_variables.order_by_global = order_by
        if asc is not None:
            global_variables.asc_global = asc

        # sorting tasks
        sort(self.tasks, asc)

        # reloading each task
        for task in self.tasks:
            self.remove_widget(task)
        for task in self.tasks:
            self.add_widget(task, 1 + len(self.disabled_tasks))

    def reload_label(self):
        # getting from database current name and priority
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute(f"SELECT label_name, priority FROM Labels WHERE ROWID = {self.rowid}")
        new_name = db.fetchone()

        # updating name
        self.label.update_name(str(new_name[0]))
        self.priority = new_name[1]
        database.close()

    # moving task from another label
    def add_task(self, task):
        # increasing widget size to make space for new task
        self.height += self.widget_height

        # adding completed task
        if task.active:
            self.disabled_tasks.append(task)
            task.opacity = .3
            if global_variables.which_label_global != 'all':
                self.add_widget(self.disabled_tasks[-1], 1)
        # adding not completed task
        else:
            self.tasks.append(task)
            # displaying task if tasks are sorted by label
            if global_variables.which_label_global != 'all':
                self.add_widget(self.tasks[-1], 1 + len(self.disabled_tasks))

    def add_photo(self, rowid, label_name):
        # changing screen to camera
        self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'camera_screen'
        # giving necessary parameters
        self.parent.parent.parent.parent.parent.ids.camera_layout.build(rowid, label_name)


class TaskLabel(BoxLayout):
    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        # parameters
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'

        # attributes
        self.info_window = None
        self.label_name = label

        # displaying widgets
        self.add_widget(Label(text=label, size_hint_x=.6))
        self.add_widget(Label(size_hint_x=.2))
        self.add_widget(MDIconButton(icon='trash-can-outline', icon_size=Window.size[1] / 40, center=(.5, .5),
                                     on_release=self.display_info_window, pos_hint={"center_x": .5, "center_y": .5}))

    # updating name in label
    def update_name(self, name):
        self.children[-1].text = name

    # remove disabled task
    def remove(self, *args):
        # calling function from Label Layout to remove disabled task
        self.parent.remove_disabled()
        # remove info window
        self.info_window.dismiss()
        self.info_window = None

    def display_info_window(self, *args):
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
        # parameters
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'

        # attributes
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
        self.trash = None
        self.back_del = None
        self.check_box = None

        # building task in label
        if type(self.active) == int:
            self.build_checkbox()
            self.build_rest()
            self.build_edit()

        # building task in trash
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
        # getting proper icon
        if self.notification:
            icon = 'bell'
        else:
            icon = 'bell-off-outline'
        time = str(self.eta)

        # getting proper eta
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
        self.add_widget(Label(size_hint_x=.01))
        self.add_widget(MDIcon(icon='numeric-{}-box-outline'.format(self.priority), size_hint_x=.1,
                               text_color=global_variables.priority_colors[self.priority - 1],
                               theme_text_color='Custom', pos_hint={"center_x": .5, "center_y": .53}))
        self.add_widget(Label(size_hint_x=.01))

        # if note is text
        if isinstance(self.note, str):
            self.add_widget(Label(text=self.note))
        # if note is image
        else:
            image_texture = ndarray_to_texture(self.note, 'luminance')
            self.add_widget(Image(texture=image_texture, pos_hint={'center_x': .5, 'center_y': .5}))

    # getting values necessary for sorting
    def value(self):
        # if sorting by priority
        if global_variables.order_by_global in ('category', 'priority'):
            return self.priority, self.deadline
        # if sorting by deadline
        elif global_variables.order_by_global == 'deadline':
            return self.deadline, self.priority

    # called when changing activity od a task
    def on_checkbox_active(self, instance, value):
        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # if marked completed
        if value:
            # saving in database
            db.execute(f"""
                            UPDATE Notes
                            SET active = 1
                            WHERE ROWID = {self.rowid};
                        """)
            database.commit()

            # updating attribute
            self.active = True
            # disabling task in LabelLayout
            self.parent.disable_task(self.rowid)
        else:
            # saving in database
            db.execute(f"""
                            UPDATE Notes
                            SET active = 0
                            WHERE ROWID = {self.rowid};
                        """)
            database.commit()

            # updating attribute
            self.active = False
            # activating task in LabelLayout
            self.parent.activate_task(self.rowid)
        database.close()

    # called when editing task
    def edit(self, *args):
        # checking if is task is not completed
        if not self.active:
            # if sorted not by labels
            if global_variables.which_label_global == 'all':
                # closing navigation drawer
                self.parent.parent.parent.parent.parent.ids.nav_drawer.set_state("close")
                # setting current screen to edit
                self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
                # giving task instance to edit
                self.parent.parent.parent.parent.parent.ids.edit_screen.build_task(self)
            # if sorted by labels
            else:
                # closing navigation drawer
                self.parent.parent.parent.parent.parent.parent.ids.nav_drawer.set_state("close")
                # setting current screen to edit
                self.parent.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
                # giving task instance to edit
                self.parent.parent.parent.parent.parent.parent.ids.edit_screen.build_task(self)

    # permanent delete of a task
    def delete_permanent(self, *args):
        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # deleting task
        db.execute(f"""DELETE FROM Trash WHERE ROWID = {self.rowid}
             """)
        database.commit()
        database.close()

        # remove task instance
        self.parent.remove_task(self)

    # restoring task from trash
    def back_delete(self, *args):
        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # auxiliary variables
        note = ''
        img = None
        shape = None

        # if note is text
        if isinstance(self.note, str):
            note = self.note
        # if note is image
        else:
            img = sqlite3.Binary(self.note)
            shape = np.array(img.shape)

        # inserting task to tasks
        db.execute("""
                        INSERT INTO Notes (label_id, priority, deadline, note, image, active, eta, notification, 
                        notification_time, shape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (self.label_id, self.priority, self.deadline, note, img, 0, self.eta, self.notification,
                              self.notification_time, shape))
        database.commit()

        # getting rowid of a task
        db.execute(""" SELECT ROWID, note FROM Notes ORDER BY ROWID DESC """)
        rowid = int(db.fetchone()[0])

        # getting label name of a task
        db.execute(f"SELECT label_name FROM Labels where ROWID = {self.label_id}")
        l_name = db.fetchone()[0]

        database.close()

        # creating task instance
        new_task = Task(l_name, self.label_id, 0, self.priority, self.note, self.notification, self.eta, self.deadline,
                        self.notification_time, rowid)

        # adding task
        self.parent.parent.parent.parent.parent.ids.main_screen.add_task(new_task)
        self.parent.parent.parent.parent.parent.ids.main_screen.labels[self.label_id].add_task(new_task)
        # updating label screen
        self.parent.parent.parent.parent.parent.ids.main_screen.update()

        # permanently deleting task from trash
        self.delete_permanent()
