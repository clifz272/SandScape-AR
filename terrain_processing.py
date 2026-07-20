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


def despeckle(height_map, blur_size=3, threshold=3.0):
    """
    Removes isolated sensor noise ("weird shapes") by comparing each
    pixel against a local blurred average. Pixels that deviate more
    than `threshold` from their neighborhood are replaced with the
    local average instead of the raw noisy value — this smooths out
    small speckle without blurring genuine terrain edges the way a
    plain global blur would.

    Note: `threshold` should be in the same units as `height_map`.
    When run on real millimetre height data, threshold is in mm, not
    the 0-255 scale.
    """

    if height_map is None:
        return None

    if blur_size % 2 == 0:
        blur_size += 1

    mean = cv2.blur(height_map, (blur_size, blur_size))
    diff = cv2.absdiff(height_map, mean)

    noise_mask = diff > threshold

    cleaned = height_map.copy()
    cleaned[noise_mask] = mean[noise_mask]

    return cleaned


def create_height_colormap(depth_map):
    if depth_map is None:
        return None

    depth_map = np.clip(depth_map, 0, 255).astype(np.uint8)

    smooth = cv2.GaussianBlur(depth_map, (5, 5), 0)

    # BGR colour points
    color_points = [
        (0,   [120, 45, 0]),       # deep water
        (20,  [210, 110, 35]),     # water
        (45,  [235, 170, 80]),     # shallow water
        (75, [190, 190, 110]),     # coast / sand
        (105, [80, 175, 80]),      # flat grass / baseline
        (120, [55, 150, 65]),      # grass
        (135, [70, 125, 90]),      # hill
        (165, [65, 95, 110]),      # darker hill
        (185, [90, 120, 150]),     # mountain / rock
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
