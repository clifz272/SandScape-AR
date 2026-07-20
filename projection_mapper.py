# projection_mapper.py

import cv2
import numpy as np

from config import (
    PROJECTOR_WIDTH,
    PROJECTOR_HEIGHT,
    PROJECTOR_X,
    PROJECTOR_Y,
    PROJECTOR_MEASURED_FULL_WIDTH_CM,
    PROJECTOR_MEASURED_FULL_HEIGHT_CM,
    PROJECTOR_CONTENT_WIDTH_CM,
    PROJECTOR_CONTENT_HEIGHT_CM,
    PROJECTOR_CONTENT_OFFSET_TOP_CM,
    PROJECTOR_CONTENT_OFFSET_LEFT_CM
)


WINDOW_NAME = "AR Sandbox Projection"

_window_ready = False
_last_fullscreen = None
_last_second_screen = None


def resize_for_projector(image):
    # Convert cm measurements to pixels using the one-time measured
    # pixels-per-cm at the current projector distance/zoom. X and Y use
    # independent ratios, since the target physical aspect ratio
    # (sandbox) generally differs from the projector's native pixel
    # aspect ratio.
    px_per_cm_x = PROJECTOR_WIDTH / PROJECTOR_MEASURED_FULL_WIDTH_CM
    px_per_cm_y = PROJECTOR_HEIGHT / PROJECTOR_MEASURED_FULL_HEIGHT_CM

    content_w = max(1, int(PROJECTOR_CONTENT_WIDTH_CM * px_per_cm_x))
    content_h = max(1, int(PROJECTOR_CONTENT_HEIGHT_CM * px_per_cm_y))

    # Clamp so the requested physical size can't exceed the projector's
    # actual resolution (would otherwise break the canvas assignment).
    content_w = min(content_w, PROJECTOR_WIDTH)
    content_h = min(content_h, PROJECTOR_HEIGHT)

    resized = cv2.resize(
        image,
        (content_w, content_h),
        interpolation=cv2.INTER_LINEAR
    )

    canvas = np.zeros((PROJECTOR_HEIGHT, PROJECTOR_WIDTH, 3), dtype=np.uint8)

    # Absolute position of the content's top-left corner, measured from
    # the full projector output's top-left corner.
    x_offset = int(PROJECTOR_CONTENT_OFFSET_LEFT_CM * px_per_cm_x)
    y_offset = int(PROJECTOR_CONTENT_OFFSET_TOP_CM * px_per_cm_y)

    # Clamp so the content can't be positioned partially or fully
    # off-canvas, which would otherwise crash the array assignment below.
    x_offset = max(0, min(x_offset, PROJECTOR_WIDTH - content_w))
    y_offset = max(0, min(y_offset, PROJECTOR_HEIGHT - content_h))

    canvas[y_offset:y_offset + content_h, x_offset:x_offset + content_w] = resized

    return canvas


def setup_projection(fullscreen=True, second_screen=False):
    """
    Setup the projection window only once.

    This avoids running namedWindow, moveWindow, resizeWindow,
    and setWindowProperty every frame.
    """

    global _window_ready, _last_fullscreen, _last_second_screen

    if (
        _window_ready
        and _last_fullscreen == fullscreen
        and _last_second_screen == second_screen
    ):
        return

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, PROJECTOR_WIDTH, PROJECTOR_HEIGHT)

    if fullscreen:
        cv2.setWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )
    else:
        cv2.setWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_NORMAL
        )

    if second_screen:
        cv2.moveWindow(WINDOW_NAME, PROJECTOR_X, PROJECTOR_Y)
    else:
        cv2.moveWindow(WINDOW_NAME, 0, 0)

    _window_ready = True
    _last_fullscreen = fullscreen
    _last_second_screen = second_screen


def show_projection(image, fullscreen=True, second_screen=False):
    setup_projection(fullscreen, second_screen)
    cv2.imshow(WINDOW_NAME, image)


def close_projection():
    global _window_ready, _last_fullscreen, _last_second_screen

    try:
        cv2.destroyWindow(WINDOW_NAME)
    except cv2.error:
        pass

    _window_ready = False
    _last_fullscreen = None
    _last_second_screen = None