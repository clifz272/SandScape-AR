# terrain_processing.py

import cv2
import numpy as np

from config import BLUR_SIZE


def smooth_depth_map(depth_map):
    """
    Light smoothing for terrain colour.
    Keep this light because this runs every frame.
    """

    if depth_map is None:
        return None

    if BLUR_SIZE <= 1:
        return depth_map

    if BLUR_SIZE % 2 == 0:
        blur_size = BLUR_SIZE + 1
    else:
        blur_size = BLUR_SIZE

    smoothed = cv2.GaussianBlur(depth_map, (blur_size, blur_size), 0)
    return smoothed



def create_height_colormap(depth_map):
    """
    Realistic-lite colour map for Raspberry Pi.

    0-90    = water
    90-120  = coast
    120-170 = grass
    170-220 = hill/rock
    220+    = mountain
    """

    if depth_map is None:
        return None

    depth_map = np.clip(depth_map, 0, 255).astype(np.uint8)

    smooth = cv2.GaussianBlur(depth_map, (5, 5), 0)

    # BGR colour points
    color_points = [
        (0,   [120, 45, 0]),       # deep water
        (20,  [210, 110, 35]),     # water
        (45,  [235, 170, 80]),     # shallow water
        (75, [190, 190, 110]),    # coast / sand
        (105, [80, 175, 80]),      # flat grass / baseline
        (120, [55, 150, 65]),      # grass
        (155, [70, 125, 90]),      # darker hill
        (175, [90, 120, 150]),     # mountain / rock
        (205, [135, 140, 160])     # high mountain, not pure white
    ]

    lut = np.zeros((256, 3), dtype=np.uint8)
    values = np.array([p[0] for p in color_points], dtype=np.float32)

    for channel in range(3):
        channel_values = np.array(
            [p[1][channel] for p in color_points],
            dtype=np.float32
        )

        lut[:, channel] = np.interp(
            np.arange(256),
            values,
            channel_values
        ).astype(np.uint8)

    colored = lut[smooth]

    colored = cv2.GaussianBlur(colored, (5, 5), 0)

    return colored
