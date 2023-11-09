import cv2
import numpy as np

from kivy.graphics.texture import Texture

from include.sort import sort_task


def sort(tasks, asc):
    sort_task(tasks)
    # reverse order
    if asc == 'desc':
        length = len(tasks)
        for i in range(int(length / 2)):
            tasks[i], tasks[length - i - 1] = tasks[length - i - 1], tasks[i]


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
        image.flip_horizontal()

    return image


def texture_to_ndarray(texture):
    image = np.frombuffer(texture.pixels, dtype='uint8')
    image.shape = (texture.size[1], texture.size[0], 4)

    return image


def ndarray_to_texture(image, color_palette='rgba'):
    buf1 = cv2.flip(image, 0)
    buf = buf1.tostring()
    image_texture = Texture.create(size=(image.shape[1], image.shape[0]))
    image_texture.blit_buffer(buf, colorfmt=color_palette, bufferfmt='ubyte')

    return image_texture
