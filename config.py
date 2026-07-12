# config.py

# =========================
# RealSense depth range
# =========================
# Depth values are in millimetres
MIN_DEPTH_MM = 300
MAX_DEPTH_MM = 1000

# =========================
# Camera resolution
# =========================
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

PROCESSING_SCALE = 0.5

# =========================
# Software depth filtering
# =========================
# Software median blur
# 3 is faster than 5 and still removes small speckles
MEDIAN_BLUR_SIZE = 3

# Software depth temporal smoothing
# Higher = smoother but more latency
# Good range: 0.45 to 0.70
DEPTH_SMOOTHING_ALPHA = 0.20

# =========================
# Terrain smoothing
# =========================
# Lower blur = lower latency
BLUR_SIZE = 3

# Adaptive height smoothing in main.py
# When sand is moving, use less smoothing.
# When sand is still, use more smoothing.
HEIGHT_SMOOTHING_STILL_WEIGHT = 0.55
HEIGHT_SMOOTHING_MOVING_WEIGHT = 0.20
MOTION_THRESHOLD_MM = 12

# =========================
# Contour settings
# =========================
SHOW_BASE_CONTOURS = False
SHOW_CHANGE_CONTOURS = True

BASE_CONTOUR_INTERVAL_MM = 10
BASE_CONTOUR_OFFSET_MM = 0

# Higher value = fewer contour levels = faster
# Try 8 first. Use 10 or 12 if still laggy.
CONTOUR_INTERVAL_MM = 28

CONTOUR_MIN_AREA = 80

# Contour line thickness in pixels
# 1 = thinnest, 2 = medium, 3+ = thick
CONTOUR_LINE_THICKNESS = 2

# =========================
# Calibration settings
# =========================
CALIBRATION_FRAMES = 120
SANDBOX_MIN_VALID_MM = 250
SANDBOX_MAX_VALID_MM = 1200
MIN_SANDBOX_AREA = 8000
HEIGHT_CHANGE_THRESHOLD_MM = 12

# =========================
# Debug settings
# =========================
# Set True only when debugging.
# Extra imshow windows can reduce FPS.
DEBUG_WINDOWS = False

# =========================
# Projector settings
# =========================
PROJECTOR_WIDTH = 854
PROJECTOR_HEIGHT = 480

# If projector is extended to the right of laptop screen,
# this is usually your laptop screen width.
PROJECTOR_X = 1920
PROJECTOR_Y = 0

# False = show on laptop/main screen
# True = move window to projector position
PROJECTOR_ON_SECOND_SCREEN = False