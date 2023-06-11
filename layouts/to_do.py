from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, NoTransition, FadeTransition, ScreenManager

from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from time import sleep
import sqlite3

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDIcon
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget, OneLineRightIconListItem, \
    ILeftBody, ILeftBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawerHeader, \
    MDNavigationDrawerLabel, MDNavigationDrawer, MDNavigationDrawerDivider, MDNavigationDrawerItem
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.widget import MDWidget

from layouts.notebook import Notebook


menu_button_ratio = 8
side_menu_button_ratio = 15
m_size_global = Window.size[0] / menu_button_ratio
s_butt_size_global = Window.size[1] / side_menu_button_ratio
TAG = 'ERROR'


class ToDoList(MDNavigationLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name FROM Labels WHERE id_default=1")
        self.items = db.fetchone()
        database.close()
        global TAG
        TAG = self.items[0]

    def get_tag(self):
        return self.tag


class NavigationDrawerScreenManager(MDScreenManager): #  tu musi być screenmanager żeby nie było laga
    pass


class MainView(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.labels = {}
        self.tasks = []
        self.order_by = 'priority'

        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT ROWID, label_name FROM Labels ORDER BY priority")
        labels = db.fetchall()  # lista krotek
        for label in labels:
            self.labels[label[1]] = TaskLabel(label[1])
            self.add_widget(self.labels[label[1]])
            db.execute("""SELECT N.active, N.priority, N.note, N.notification, N.eta, N.deadline
            FROM Labels AS L LEFT JOIN Notes AS N ON L.ROWID = N.label_id
            WHERE N.label_id = {} ORDER BY N.active, N.priority, N.deadline""".format(label[0]))
            items = db.fetchall()
            for i in items:
                self.tasks.append(Task(label[1], str(label[0]), i[0], i[1], i[2], i[3], i[4], i[5]))
                # self.add_widget(Button(text=str(i), size_hint_y = None, height = Window.size[1] / 13))
                self.add_widget(self.tasks[-1])
        # self.remove_widget(self.labels[1])
        database.close()

    def update(self, order_by, which_label):
        self.clear_widgets()
        if order_by != self.order_by:
            pass  # tu trzeba sortowanie
        if which_label == 'all':
            for task in self.tasks:
                self.add_widget(task)
        if which_label == 'category':
            idx = 0
            for name in self.labels.keys():
                self.add_widget(self.labels[name])
                while idx < len(self.tasks) and self.tasks[idx].name == name:
                    self.add_widget(self.tasks[idx])
                    idx += 1
        else:
            for task in self.tasks:
                if task.label_id == which_label:
                    self.add_widget(task)


class TaskLabel(BoxLayout):
    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'
        self.add_widget(Label(text=label, size_hint_x=.6))
        self.add_widget(Label(size_hint_x=.2))
        self.add_widget(MDIconButton(icon='trash-can-outline', icon_size=Window.size[1] / 40,
                                     center=(.5, .5), on_release=self.press))

    def press(self, but):
        print(but.icon)


class Task(BoxLayout):
    def __init__(self, label_name, label_id, active, priority, note, notification, eta, deadline, **kwargs):
        super().__init__(**kwargs)
        self.label_id = label_id
        self.name = label_name
        self.priority = priority
        self.eta = eta
        self.deadline = deadline
        self.note = note

        priority_colors = [(1,0,0,.9), (245/255,118/255,39/255,0.8), (245/255,217/255,39/255,0.8), (47/255,151/255,33/255,0.8)]
        self.size_hint_y = None
        self.height = Window.size[1] / 13
        self.orientation = 'horizontal'
        self.add_widget(CheckBox(size_hint_x=.1, active=active))
        self.add_widget(Label(size_hint_x=.01))
        self.add_widget(MDIcon(icon='numeric-{}-box-outline'.format(priority), size_hint_x=.1,
                               text_color=priority_colors[priority-1], theme_text_color='Custom',
                               pos_hint={"center_x": .5, "center_y": .53}))
        self.add_widget(Label(text=note))
        if notification:
            icon = 'bell'
        else:
            icon = 'bell-off-outline'
        if eta:
            time = '~'+str(eta)+'min'
        else:
            time = '~'
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

    def press(self, but):
        print(but.text)

    def edit(self, but):
        self.parent.parent.parent.parent.parent.ids.nav_drawer.set_state("close")
        self.parent.parent.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        self.parent.parent.parent.parent.parent.ids.edit_screen.edit_task(self)


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
            self.parent.parent.parent.ids.main_screen.update('priority', butt.id)


class EditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touched_id = None
        self.absolute_pos_0 = None
        self.widget_y_0 = None
        self.labels = []

        self.widget_height = Window.size[0]*.1
        self.edit_window = MDRelativeLayout()
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

    def edit_label(self, rowid, label_name):
        self.window.height += self.widget_height
        self.edit_window.add_widget(MDTextField(id=str(rowid), text=label_name, size_hint_y=None, text_color_focus='white',
                                           line_color_focus='white', height=self.widget_height, required=True))
        self.save_button.bind(on_release=self.save_label)

    def edit_all_labels(self):
        self.save_button.bind(on_release=self.save_labels)
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

    def add_label(self):
        pass

    def edit_task(self, task):
        self.save_button.bind(on_release=self.save_tasks)

    def exit(self, butt):
        self.edit_window.clear_widgets()
        self.window.height = Window.size[0] * .15
        self.parent.current = 'screen'

    def save_labels(self, butt):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        for idx, label_tuple in enumerate(self.labels, 1):
            db.execute("""
                        UPDATE Labels
                        SET priority = {}, label_name = {}
                        WHERE ROWID = {};
                    """.format(len(self.labels)-idx, '"'+label_tuple[0].ids[str(label_tuple[1])].text+'"', label_tuple[1]))
            database.commit()
        database.close()

        self.labels = []
        self.parent.parent.ids.md_list_nav_drawer.reload()
        self.exit(butt)
        self.save_button.unbind(on_release=self.save_labels)
        # TODO tu trzeba dodać żeby aktualizowało MainView (gdy jest w trybie category)
        # print('save-labels')

    def save_label(self, but):
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        db.execute("""
                        UPDATE Labels
                        SET label_name = {}
                        WHERE ROWID = {};
                    """.format('"'+self.edit_window.children[0].text+'"', self.edit_window.children[0].id))
        database.commit()
        database.close()

        self.parent.parent.ids.md_list_nav_drawer.reload()
        self.exit(but)
        self.save_button.unbind(on_release=self.save_label)

    def save_tasks(self, butt):

        self.exit(butt)
        self.save_button.unbind(on_release=self.save_tasks)
        # print('save-tasks')

