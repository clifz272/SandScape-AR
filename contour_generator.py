# contour_generator.py

import cv2
import numpy as np

from config import (
    CONTOUR_INTERVAL_MM,
    BASE_CONTOUR_INTERVAL_MM,
    BASE_CONTOUR_OFFSET_MM,
    CONTOUR_MIN_AREA,
    CONTOUR_LINE_THICKNESS
)


def generate_contour_overlay_from_height_change(height_map_8bit, output_shape):
    """
    Very fast synced topography lines for Raspberry Pi.

    This expects the same 0-255 height map used for the terrain colour.
    Because main.py passes smoothed_depth into this function, the lines
    stay synced with the map.
    """

    h, w = output_shape[:2]
    contour_overlay = np.zeros((h, w, 3), dtype=np.uint8)

    if height_map_8bit is None:
        return contour_overlay

    height_map = np.nan_to_num(height_map_8bit).astype(np.uint8)

    if height_map.shape[:2] != (h, w):
        height_map = cv2.resize(
            height_map,
            (w, h),
            interpolation=cv2.INTER_LINEAR
        )

    # Use height bands instead of cv2.findContours.
    # This is much faster on Raspberry Pi.
    interval = max(12, int(CONTOUR_INTERVAL_MM))
    bands = (height_map // interval).astype(np.uint8)

    line_mask = np.zeros_like(height_map, dtype=np.uint8)

    # Detect where neighbouring pixels move into a different height band
    line_mask[:, 1:] |= (bands[:, 1:] != bands[:, :-1]).astype(np.uint8) * 255
    line_mask[1:, :] |= (bands[1:, :] != bands[:-1, :]).astype(np.uint8) * 255

    # Controllable line thickness
    if CONTOUR_LINE_THICKNESS > 1:
        kernel = np.ones((CONTOUR_LINE_THICKNESS, CONTOUR_LINE_THICKNESS), np.uint8)
        line_mask = cv2.dilate(line_mask, kernel, iterations=1)

    # Near-black line.
    # Do not use pure (0,0,0), because main.py detects overlay pixels using > 0.
    contour_overlay[line_mask > 0] = (5, 5, 5)

    return contour_overlay


def generate_base_contours_from_depth(depth_mm, base_image):
    """
    Generate base contour lines from actual depth.
    Usually disabled for better performance.
    """

    contour_image = base_image.copy()

    if depth_mm is None:
        return contour_image

    depth_mm = np.nan_to_num(depth_mm).astype(np.float32)

    depth_mm = cv2.GaussianBlur(depth_mm, (5, 5), 0)

    min_d = int(np.min(depth_mm))
    max_d = int(np.max(depth_mm))

    for level in range(
        min_d + BASE_CONTOUR_OFFSET_MM,
        max_d,
        BASE_CONTOUR_INTERVAL_MM
    ):
        level_mask = np.uint8(depth_mm <= level) * 255

        contours, _ = cv2.findContours(
            level_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < CONTOUR_MIN_AREA:
                continue

            cv2.drawContours(
                contour_image,
                [contour],
                -1,
                (180, 180, 180),
                1,
                lineType=cv2.LINE_AA
            )

    return contour_image
