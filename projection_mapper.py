# projection_mapper.py

import cv2

from config import (
    PROJECTOR_WIDTH,
    PROJECTOR_HEIGHT,
    PROJECTOR_X,
    PROJECTOR_Y
)


WINDOW_NAME = "AR Sandbox Projection"

_window_ready = False
_last_fullscreen = None
_last_second_screen = None


def resize_for_projector(image):
    return cv2.resize(
        image,
        (PROJECTOR_WIDTH, PROJECTOR_HEIGHT),
        interpolation=cv2.INTER_LINEAR
    )


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

    if second_screen:
        cv2.moveWindow(WINDOW_NAME, PROJECTOR_X, PROJECTOR_Y)
    else:
        cv2.moveWindow(WINDOW_NAME, 0, 0)

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