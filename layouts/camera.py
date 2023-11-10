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
    def build(self, rowid, label_name):
        self.rowid = rowid
        self.label_name = label_name
        self.md_bg_color = (0, 0, 0, 1)
        icon_size = Window.size[0]/8
        self.add_widget(MDIconButton(pos_hint={'center_x': .5}, icon='camera-outline', size_hint=(None, None),
                               on_release=lambda x: self.take_photo(), icon_size=icon_size,
                               md_bg_color=(32/255, 3/255, 252/255, 1)))
        self.camera = TaskCamera(play=True, keep_ratio=True, allow_stretch=True)
        self.add_widget(self.camera)

    def take_photo(self):
        self.camera.play = False
        self.clear_widgets()

        self.edit_grid = EditPhoto(self.camera.texture, md_bg_color=(1, 1, 1, .1), size_hint=(1, .8),
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
        # self.texture = cv2.imread('images/x_cut.jpg')
        # plt.imshow(self.image1, 'gray') luminance
        # plt.axis('off')
        # plt.show()
        #
        # buf1 = cv2.flip(self.image1, 0)
        # buf = buf1.tostring()
        # image_texture = Texture.create(size=(self.image1.shape[1], self.image1.shape[0]), colorfmt='bgr')
        # image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.texture = texture
        if usage == 'cut':
            self.texture = rotate_image_right(self.texture)
        else:
            self.texture.flip_vertical()
            self.texture.flip_horizontal()
        #print(texture.size)

        self.photo = Image(texture=self.texture, size_hint=(.9, .9), pos_hint={'center_x': .5, 'center_y': .5},
                           keep_ratio=True, allow_stretch=True)
        print(self.photo.width)
        # print(self.texture)

        self.add_widget(self.photo)

        img_ratio = self.texture.size[0] / self.texture.size[1]  # width / height
        window_ratio = Window.size[0] / (Window.size[1] * .8)

        if img_ratio > window_ratio:
            self.im_width = Window.size[0] * .9
            self.im_height = self.im_width/img_ratio

        else:
            self.im_height = Window.size[1] * .8 * .9
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
        image = texture_to_ndarray(self.texture)
        # image = image[0:-1, 0:-1, 0:3]
        # plt.imshow(image)
        # plt.axis('off')
        # plt.show()
        # print(image.shape)
        # print(type(image))
        # print(type(image[0][0][0]))
        # image2 = cv2.imread('images/x_cut.jpg')
        # print(image2.shape)
        # print(type(image2))
        # print(type(image2[0][0][0]))

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # plt.imshow(image_bin, 'gray')
        # plt.axis('off')
        # plt.show()

        (h, w) = image_gray.shape[:2]
        width = 1000  # TODO jakoś powiącać inaczej
        r = width / float(w)
        dim = (width, int(h * r))
        img = cv2.resize(image_gray, dim, interpolation=cv2.INTER_AREA)
        nr = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        image_bin = np.where(img < nr[0], 0, 1)

        ratio_break = []
        first_white = -1
        for curr_line in range(image_bin.shape[0]):
            for col in range(image_bin.shape[1]):
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

        image = texture_to_ndarray(self.texture)
        image = image[0:int(self.texture.size[1]), int(self.texture.size[0] * ratio_x[0]):int(self.texture.size[0] * ratio_x[1])]
        texture_cut = ndarray_to_texture(image)

        self.clear_widgets()
        self.texture = None
        self.lines = []
        self.add_photo('divide', texture_cut)

    def save_all(self):
        task_images = []
        prev_ratio = 0
        image = texture_to_ndarray(self.texture)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        (h, w) = image_gray.shape[:2]
        width = 1000
        r = width / float(w)
        dim = (width, int(h * r))
        image_gray = cv2.resize(image_gray, dim, interpolation=cv2.INTER_AREA)

        nr = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        for row in range(image_gray.shape[0]):
            for col in range(image_gray.shape[1]):
                if image_gray[row][col] > nr[0]:
                    image_gray[row][col] = 0
                else:
                    image_gray[row][col] = 255

        for line in self.lines:
            curr_ratio = (self.ymax - line.y) / self.im_height
            img_cut = image_gray[int(image_gray.shape[0] * prev_ratio):int(image_gray.shape[0] * curr_ratio),  \
                                                                                                0:int(image_gray.shape[1])]
            task_images.append(img_cut)
            prev_ratio = curr_ratio

        img_cut = image_gray[int(image_gray.shape[0] * prev_ratio):image_gray.shape[0], 0:int(image_gray.shape[1])]
        task_images.append(img_cut)

        return task_images

    def on_touch_down(self, touch):
        for i in range(len(self.lines)):
            if (self.lines[i].x-self.lines[i].w_size[0]*2) <= touch.x <= self.lines[i].x+self.lines[i].w_size[0]*2 \
                    and (self.lines[i].y-self.lines[i].w_size[1]*2) <= touch.y <= self.lines[i].y+self.lines[i].w_size[1]*2:
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
        radius = 15
        size += 36*3
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
                self.circle[0] = Line(circle=(p1[0], p1[1], radius), width=radius * .2)
                self.circle[1] = Line(circle=(p2[0], p2[1], radius), width=radius * .2)

        else:
            if Window.size[0] > size:
                self.w_size = (size, radius*1.1)
                self.x += (Window.size[0] - size)/2
            else:
                self.w_size = (Window.size[0], radius*1.1)

            self.size = self.w_size

            p1 = (self.x+radius*.5, self.y)
            p2 = (self.x+self.width-(.5*radius), self.y)
            with self.canvas:
                Color(1, 0, 0)
                self.line = Line(points=[p1[0]+radius, p1[1], p2[0]-radius, p2[1]], width=radius * .2)
                self.circle[0] = Line(circle=(p1[0], p1[1], radius), width=radius * .2)
                self.circle[1] = Line(circle=(p2[0], p2[1], radius), width=radius * .2)

    def update_pos(self, pos):
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