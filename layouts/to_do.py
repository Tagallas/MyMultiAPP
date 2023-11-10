from kivy.core.window import Window
import sqlite3

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget, OneLineRightIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawerHeader, MDNavigationDrawerDivider
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

# tag in TopAppBar
TAG = 'TO DO'


# MAIN SCREEN
class ToDoList(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # tag in TopAppBar
        global TAG
        self.items = TAG
        # height of a single task
        self.task_height = Window.size[1] / 30

    def get_tag(self):
        return self.tag

    # Called by dropdown menu to sort tasks
    def sort_tasks(self):
        self.sort_menu = MDDropdownMenu(caller=self.ids.app_bar, items=self.create_sort_items(),
                                        width_mult=2.3, max_height=self.task_height * 5 + 80)
        self.sort_menu.open()

    # Dialog with confirmation to delete tasks from trash
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

    # called when deleting tasks from trash
    def delete_trash(self, *args):
        # dismissing dialog
        self.info_window.dismiss()

        # clearing screen
        self.ids.trash_can_view.clear_widgets()
        self.info_window = None

        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # removing all tasks from trash database
        db.execute("""DELETE FROM Trash
             """)
        database.commit()
        database.close()

    # items to sort tasks
    def create_sort_items(self):
        return [{
                "viewclass": "MDRectangleFlatIconButton",
                "icon": 'sort',
                "text": "category",
                "halign": "left",
                "icon_size": self.task_height,
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
                "icon_size": self.task_height,
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
                "icon_size": self.task_height,
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
                "icon_size": self.task_height,
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
                "icon_size": self.task_height,
                "text_color": (1, 1, 1, 1),
                "icon_color": (1, 1, 1, 1),
                "line_color": (1, 1, 1, 0),
                "theme_text_color": 'Custom',
                "on_release": lambda x=('deadline', None, 'desc'): {self.ids.main_screen.update(x[0], x[1], x[2]),
                                                                    self.sort_menu.dismiss()}
                }]


# Defined there to reduce lag
class NavigationDrawerScreenManager(MDScreenManager):
    pass


class CustomNavigationDrawer(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # builds widget
        self.reload()

    def reload(self):
        # clearing widgets in case there are any
        self.clear_widgets()
        global TAG
        # display widget with Tag
        self.add_widget(MDNavigationDrawerHeader(title=TAG, padding=(0, 0, 0, 10)))
        self.add_widget(MDNavigationDrawerDivider())

        # display calendar button
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="calendar", on_release=self.print, text='bell'),
                                            text="Calendar", text_color=(.7, .7, .7, .5),
                                            on_release=self.calendar_open, divider=None))
        self.add_widget(MDNavigationDrawerDivider())

        # display labels header
        self.add_widget(OneLineRightIconListItem(IconRightWidget(icon="playlist-edit", on_release=self.edit_label,
                                                                 text='all',),
                                                 text="Labels", on_release=self.task_by_labels, divider=None))

        # connecting to database to get labels
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()
        db.execute("SELECT label_name, ROWID FROM Labels ORDER BY priority")
        items = db.fetchall()
        database.close()

        # for every label
        for el in items:
            # display label
            self.add_widget(OneLineIconListItem(IconLeftWidget(icon="label-outline", on_release=self.edit_label,
                                                               text=el[0], id=str(el[1])),
                                                id=str(el[1]), text=el[0], text_color=(.7, .7, .7, .5),
                                                on_release=self.task_by_labels, divider=None))

        # display Widget that adds new Label
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="plus", on_release=self.edit_label, text='Add Label'),
                                            text='Add Label', text_color=(.5, .5, .5, .5),
                                            on_release=self.edit_label, divider=None))
        self.add_widget(MDNavigationDrawerDivider())

        # display Settings button
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="cog", on_release=self.print, text='cog'),
                                            text='Settings', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))

        # display Trash Can button
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="trash-can-outline", on_release=self.trash_open,
                                                           text='trash-can'),
                                            text='Trash', text_color=(.7, .7, .7, .5),
                                            on_release=self.trash_open, divider=None))

        # display Help button
        self.add_widget(OneLineIconListItem(IconLeftWidget(icon="help-circle-outline", on_release=self.print,
                                                           text='help'),
                                            text='Help', text_color=(.7, .7, .7, .5),
                                            on_release=self.print, divider=None))

    # prints button text if is unused
    def print(self, butt):
        print(butt.text)

    # opening calendar
    def calendar_open(self, *args):
        # closing navigation drawer
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        # building calendar view
        self.parent.parent.parent.ids.calendar_view.build_daily()
        # changing screen to main
        self.parent.parent.parent.ids.screen_manager.current = 'calendar'

    # opening trash
    def trash_open(self, *args):
        # closing navigation drawer
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        # building trash can view
        self.parent.parent.parent.ids.trash_can_view.build()
        # changing screen to main
        self.parent.parent.parent.ids.screen_manager.current = 'trash_can'

    # opening edit label
    def edit_label(self, but):
        # closing navigation drawer
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        # changing screen to edit
        self.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        # when editing all labels
        if but.text == 'all':
            self.parent.parent.parent.ids.edit_screen.edit_all_labels()
        # when adding new label
        elif but.text == 'Add Label':
            self.parent.parent.parent.ids.edit_screen.add_label()
        # when editing one label
        else:
            self.parent.parent.parent.ids.edit_screen.edit_label(int(but.id), but.text)

    # displaying and sorting all tasks by labels
    def task_by_labels(self, butt):
        # changing screen to main
        self.parent.parent.parent.ids.screen_manager.current = 'screen'
        # closing navigation drawer
        self.parent.parent.parent.ids.nav_drawer.set_state("close")
        # when displaying all labels
        if butt.text == 'Labels':
            self.parent.parent.parent.ids.main_screen.update('category', 'category')
        # when displaying one label
        else:
            self.parent.parent.parent.ids.main_screen.update('priority', int(butt.id), 'asc')
