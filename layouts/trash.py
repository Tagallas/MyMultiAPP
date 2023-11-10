import numpy as np
import sqlite3

from kivymd.uix.boxlayout import MDBoxLayout


from layouts.labels import Task


class TrashCanView(MDBoxLayout):
    def build(self):
        # clearing previous widgets
        self.clear_widgets()
        self.tasks = []

        # connecting to database
        database = sqlite3.connect('databases/to_do.db')
        db = database.cursor()

        # selecting all deleted tasks
        db.execute("""SELECT priority, deadline, note, eta, notification, notification_time, deleted_date, ROWID, 
             label_id, image, shape
             FROM Trash 
             ORDER BY deleted_date""")
        items = db.fetchall()

        # for every task
        for i in items:
            # creating task widget
            # when note is text
            if i[10] is None:
                self.tasks.append(Task(None, i[8], i[6], i[0], i[2], i[4], i[3], i[1], i[5], i[7]))
            # when note is image
            else:
                shape = np.frombuffer(i[10], dtype='int32')
                img = np.frombuffer(i[9], dtype=np.uint8)
                img.shape = shape
                self.tasks.append(Task(None, i[8], i[6], i[0], img, i[4], i[3], i[1], i[5], i[7]))

            # displaying task
            self.add_widget(self.tasks[-1])

        database.close()

    # removing specific task
    def remove_task(self, task):
        self.remove_widget(task)
        self.tasks.remove(task)
