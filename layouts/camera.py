from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Color, Line
from kivy.uix.camera import Camera
from kivy.graphics.context_instructions import PushMatrix, Rotate, PopMatrix

import cv2
import numpy as np

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.floatlayout import MDFloatLayout

from include.function import rotate_image_right, texture_to_ndarray, ndarray_to_texture


class CameraLayout(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # attributes
        self.rowid = None
        self.label_name = None
        self.camera = None

    def build(self, rowid, label_name):
        self.rowid = rowid
        self.label_name = label_name
        self.md_bg_color = (0, 0, 0, 1)
        icon_size = Window.size[0] / 8

        # creating and displaying take photo button
        self.add_widget(MDIconButton(pos_hint={'center_x': .5}, icon='camera-outline', size_hint=(None, None),
                                     on_release=lambda x: self.take_photo(), icon_size=icon_size,
                                     md_bg_color=(32 / 255, 3 / 255, 252 / 255, 1)))

        # creating camera widget
        self.camera = TaskCamera(play=True, keep_ratio=True, allow_stretch=True)
        # displaying camera widget
        self.add_widget(self.camera)

    # called when taking photo
    def take_photo(self):
        # reset view
        self.camera.play = False
        self.clear_widgets()

        # creating and displaying Photo to modify it
        self.edit_grid = EditPhoto(self.camera.texture, md_bg_color=(1, 1, 1, .1), size_hint=(1, .8),
                                   pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(self.edit_grid)

        # displaying buttons to save cut or leave camera
        self.add_widget(MDBoxLayout(
            MDFlatButton(text='CANCEL', on_release=lambda x: self.exit(), size_hint_min=(None, None), size_hint=(.5, 1),
                         font_size=Window.size[1] * .03),
            MDFlatButton(text='SAVE', on_release=self.save_cut, size_hint_min=(None, None), size_hint=(.5, 1),
                         font_size=Window.size[1] * .03),
            orientation='horizontal', size_hint=(1, .1)
        ))

    # called after first (horizontal) cut
    def save_cut(self, *args):
        # rebinding button to save photo
        self.children[0].children[0].unbind(on_release=self.save_cut)
        self.children[0].children[0].bind(on_release=self.save_all)

        # displaying buttons to add or delete horizontal lines that cut photo to tasks
        self.add_widget(MDBoxLayout(
            MDIconButton(icon='minus', on_release=lambda x: self.edit_grid.remove_horizontal(),
                         size_hint_min=(None, None), size_hint=(.5, 1), icon_size=Window.size[1] * .06),
            MDIconButton(icon='plus', on_release=lambda x: self.edit_grid.add_horizontal(),
                         size_hint_min=(None, None), size_hint=(.5, 1), icon_size=Window.size[1] * .06),
            orientation='horizontal', size_hint=(1, .1), pos_hint={'top': 1}))

        # calling function that saves cut from Photo Layout
        self.edit_grid.save_cut()

    # called after second (vertical cut)
    def save_all(self, *args):
        # getting tasks images
        images = self.edit_grid.save_all()

        # clearing screen
        self.clear_widgets()

        # changing screen to add new tasks
        self.parent.parent.parent.ids.screen_manager.current = 'edit_screen'
        self.parent.parent.parent.ids.edit_screen.add_img_tasks(images, self.rowid, self.label_name)

    # called when exiting Camera Layout
    def exit(self):
        self.clear_widgets()
        self.parent.parent.parent.ids.screen_manager.current = 'screen'


# Layout in which photo is displayed
class EditPhoto(MDFloatLayout):
    def __init__(self, texture, **kwargs):
        super().__init__(**kwargs)
        # attributes
        # number of max horizontal lines you can add in second cut
        self.max_lines = 15
        self.lines_addition = 50
        # displayed texture
        self.texture = None
        # touched line index
        self.line_idx = None

        # build function
        self.add_photo('cut', texture)

    def add_photo(self, usage, texture):  # texture.size = width / height
        self.texture = texture
        # if first (horizontal cut)
        if usage == 'cut':
            # rotating image (on android camera is displayed rotated 90 degrees, this function rotates texture taken by
            # -90 degrees)
            self.texture = rotate_image_right(self.texture)
        # if second (vertical cut)
        else:
            # after conversion to ndarray texture is flipped, this functions flip it back
            self.texture.flip_vertical()
            self.texture.flip_horizontal()

        # creating image widget
        self.photo = Image(texture=self.texture, size_hint=(.9, .9), pos_hint={'center_x': .5, 'center_y': .5},
                           keep_ratio=True, allow_stretch=True)
        # displaying image
        self.add_widget(self.photo)

        # texture ratio (width / height)
        img_ratio = self.texture.size[0] / self.texture.size[1]
        # window on which image will be displayed ratio (width / height)
        window_ratio = Window.size[0] / (Window.size[1] * .8)

        # calculating both ratios to know if width or height is a cut-off value when we stretch image as much as
        # possible
        # if cut-off value is width
        if img_ratio > window_ratio:
            # displayed image width
            self.im_width = Window.size[0] * .9
            # displayed image height
            self.im_height = self.im_width / img_ratio
        # if cut-off value is height
        else:
            # displayed image height
            self.im_height = Window.size[1] * .8 * .9
            # displayed image width
            self.im_width = self.im_height * img_ratio

        # image x 0 in pixels
        self.x0 = (Window.size[0] / 2) - (self.im_width / 2)
        # image x max in pixels
        self.x_max = (Window.size[0] / 2) + (self.im_width / 2)

        # image y 0 in pixels
        self.y0 = (Window.size[1] / 2) - (self.im_height / 2)
        # image y max in pixels
        self.y_max = (Window.size[1] / 2) + (self.im_height / 2)

        # if first cut (horizontal)
        if usage == 'cut':
            # add vertical lines
            self.lines_vertical()
        # if second cut (vertical)
        elif usage == 'divide':
            # add horizontal lines
            self.lines_horizontal()

    def lines_horizontal(self):
        # converting texture to gray ndarray
        image = texture_to_ndarray(self.texture)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # resizing image to 1000 pixels width
        (h, w) = image_gray.shape[:2]
        width = 1000
        r = width / float(w)
        dim = (width, int(h * r))
        img = cv2.resize(image_gray, dim, interpolation=cv2.INTER_AREA)
        nr = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # converting pixel scale 0-255 to 0-1
        image_bin = np.where(img < nr[0], 0, 1)

        # algorithm that calculates y level of a horizontal lines (interval between tasks)
        ratio_break = []
        first_white = -1
        for curr_line in range(image_bin.shape[0]):
            for col in range(image_bin.shape[1]):
                # if black pixel
                if image_bin[curr_line][col] == 0:
                    if first_white > 0:
                        curr_ratio = ((curr_line - first_white) / 2 + first_white) / image_bin.shape[0]
                        if ratio_break == [] or (curr_ratio - ratio_break[-1] > .05):
                            ratio_break.append(curr_ratio)
                        first_white = -1
                    break
            else:
                if first_white == -1:
                    first_white = curr_line

        # adding horizontal lines
        for ratio in ratio_break:
            self.add_horizontal(ratio)

    # add horizontal line
    def add_horizontal(self, ratio=1):
        # if maximum numbers of lines is not exceeded
        if len(self.lines) < self.max_lines:
            # calculating relative y level
            y = self.y_max - ((self.y_max - self.y0) * ratio)

            # displaying cut line
            self.lines.append(CutLine('horizontal', self.im_width, y=y))
            self.add_widget(self.lines[-1])

    # remove last horizontal line
    def remove_horizontal(self):
        # if any horizontal line exists
        if self.lines:
            # remove last line
            self.remove_widget(self.lines[-1])
            del self.lines[-1]

    # add vertical lines
    def lines_vertical(self):
        # creating and displaying vertical lines (on both edges of a photo)
        self.lines = [CutLine('vertical', self.im_height, x=self.x0),
                      CutLine('vertical', self.im_height, x=self.x_max)]
        self.add_widget(self.lines[0])
        self.add_widget(self.lines[1])

    # called when saving first (horizontal) cut
    def save_cut(self):
        # calculating new image ratio
        ratio_x = []
        for line in self.lines:
            ratio_x.append((line.x - self.x0) / self.im_width)

        # cutting texture
        image = texture_to_ndarray(self.texture)
        image = image[0:int(self.texture.size[1]), int(self.texture.size[0] * ratio_x[0]):int(self.texture.size[0] *
                                                                                              ratio_x[1])]
        texture_cut = ndarray_to_texture(image)

        # clearing screen
        self.clear_widgets()
        self.texture = None
        self.lines = []

        # building screen for second cut
        self.add_photo('divide', texture_cut)

    # called when saving second (vertical) cut
    def save_all(self):
        # list of task images
        task_images = []
        prev_ratio = 0

        # converting texture to gray ndarray
        image = texture_to_ndarray(self.texture)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # resizing image to 1000 pixels width
        (h, w) = image_gray.shape[:2]
        width = 1000
        r = width / float(w)
        dim = (width, int(h * r))
        image_gray = cv2.resize(image_gray, dim, interpolation=cv2.INTER_AREA)
        nr = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # converting image colors (from white background to black)
        for row in range(image_gray.shape[0]):
            for col in range(image_gray.shape[1]):
                if image_gray[row][col] > nr[0]:
                    image_gray[row][col] = 0
                else:
                    image_gray[row][col] = 255

        # cutting out each task image
        for line in self.lines:
            # calculating ratio
            curr_ratio = (self.y_max - line.y) / self.im_height
            # cutting task image
            img_cut = image_gray[int(image_gray.shape[0] * prev_ratio):int(image_gray.shape[0] * curr_ratio),
                      0:int(image_gray.shape[1])]

            # adding task image
            task_images.append(img_cut)
            prev_ratio = curr_ratio

        img_cut = image_gray[int(image_gray.shape[0] * prev_ratio):image_gray.shape[0], 0:int(image_gray.shape[1])]
        task_images.append(img_cut)

        # return list of task images
        return task_images

    def on_touch_down(self, touch):
        # checking if line (and which line) was touched
        for i in range(len(self.lines)):
            if (self.lines[i].x - self.lines[i].w_size[0] * 2) <= touch.x <= self.lines[i].x + self.lines[i].w_size[
                0] * 2 \
                    and (self.lines[i].y - self.lines[i].w_size[1] * 2) <= touch.y <= self.lines[i].y + \
                    self.lines[i].w_size[1] * 2:
                # saving touched line idx
                self.line_idx = i

    def on_touch_up(self, touch):
        # removing touched line idx
        self.line_idx = None

    def on_touch_move(self, touch):
        # if line is touched
        if self.line_idx is not None:
            line = self.lines[self.line_idx]

            # if first (horizontal) cut
            if line.orientation == 'vertical':
                # preventing moving line out of photo
                if touch.x > self.x_max:
                    touch.x = self.x_max
                elif touch.x < self.x0:
                    touch.x = self.x0

                # updating line position
                line.x = touch.x
                line.update_pos(touch.x)

                # swapping lines in table if line moved over another line and updating touched line idx
                if self.line_idx > 0 and self.lines[self.line_idx - 1].x > line.x:
                    self.lines[self.line_idx], self.lines[self.line_idx - 1] = self.lines[self.line_idx - 1], \
                                                                               self.lines[self.line_idx]
                    self.line_idx -= 1
                elif self.line_idx < len(self.lines) - 1 and self.lines[self.line_idx + 1].x < line.x:
                    self.lines[self.line_idx], self.lines[self.line_idx + 1] = self.lines[self.line_idx + 1], \
                                                                               self.lines[self.line_idx]
                    self.line_idx += 1
            # second (vertical) cut
            else:
                # preventing moving line out of photo
                if touch.y > self.y_max:
                    touch.y = self.y_max
                elif touch.y < self.y0:
                    touch.y = self.y0

                # updating line position
                line.y = touch.y
                line.update_pos(touch.y)

                # swapping lines in table if line moved over another line and updating touched line idx
                if self.line_idx > 0 and self.lines[self.line_idx - 1].y < line.y:
                    self.lines[self.line_idx], self.lines[self.line_idx - 1] = self.lines[self.line_idx - 1], \
                                                                               self.lines[self.line_idx]
                    self.line_idx -= 1
                elif self.line_idx < len(self.lines) - 1 and self.lines[self.line_idx + 1].y > line.y:
                    self.lines[self.line_idx], self.lines[self.line_idx + 1] = self.lines[self.line_idx + 1], \
                                                                               self.lines[self.line_idx]
                    self.line_idx += 1


class CutLine(MDBoxLayout):
    def __init__(self, orientation, size, **kwargs):
        super().__init__(**kwargs)
        # parameters
        self.orientation = orientation

        # attributes
        radius = 15
        size += 36 * 3
        self.circle = [None, None]

        # if vertical line
        if orientation == 'vertical':
            # attributes
            size += 9
            self.y = Window.size[1] * .1

            # cutting line size if line moves out of window
            if Window.size[1] * .8 > size:
                self.w_size = (radius * 1.1, size)
                self.y += (Window.size[1] * .8 - size) / 2
            else:
                self.w_size = (radius * 1.1, Window.size[1] * .8)

            self.size = self.w_size

            # declaring line ending points
            p1 = (self.x, self.y + radius * 2)
            p2 = (self.x, self.y + self.height - (2 * radius))

            with self.canvas:
                # line color - red
                Color(1, 0, 0)
                # displaying line and circle in both ends
                self.line = Line(points=[p1[0], p1[1] + radius, p2[0], p2[1] - radius], width=radius * .2)
                self.circle[0] = Line(circle=(p1[0], p1[1], radius), width=radius * .2)
                self.circle[1] = Line(circle=(p2[0], p2[1], radius), width=radius * .2)

        # if horizontal line
        else:
            # cutting line size if line moves out of window
            if Window.size[0] > size:
                self.w_size = (size, radius * 1.1)
                self.x += (Window.size[0] - size) / 2
            else:
                self.w_size = (Window.size[0], radius * 1.1)

            self.size = self.w_size

            # declaring line ending points
            p1 = (self.x + radius * .5, self.y)
            p2 = (self.x + self.width - (.5 * radius), self.y)
            with self.canvas:
                # line color - red
                Color(1, 0, 0)
                # displaying line and circle in both ends
                self.line = Line(points=[p1[0] + radius, p1[1], p2[0] - radius, p2[1]], width=radius * .2)
                self.circle[0] = Line(circle=(p1[0], p1[1], radius), width=radius * .2)
                self.circle[1] = Line(circle=(p2[0], p2[1], radius), width=radius * .2)

    # updating line position
    def update_pos(self, pos):
        # if vertical line
        if self.orientation == 'vertical':
            # updating line ending points
            self.line.points = (pos, self.line.points[1], pos, self.line.points[3])
            # updating both circle positions
            for circle in self.circle:
                circle.circle = (pos, circle.circle[1], circle.circle[2])
        # if horizontal line
        else:
            # updating line ending points
            self.line.points = (self.line.points[0], pos, self.line.points[2], pos)
            # updating both circle positions
            for circle in self.circle:
                circle.circle = (circle.circle[0], pos, circle.circle[2])

    # getting line position
    def get_pos(self):
        # if vertical line
        if self.orientation == 'vertical':
            # getting x position (moved by 3 to get middle position)
            return self.x + 3
        # if horizontal line
        else:
            # getting y position (moved by 3 to get middle position)
            return self.y + 3


class TaskCamera(Camera):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # parameters
        self.index = 0

        # rotating camera -90 degrees (on android camera is rotated 90 degrees to see it in a correct way
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=(-90), origin=[Window.size[0] / 2, Window.size[1] / 2])
        with self.canvas.after:
            PopMatrix()
