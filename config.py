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
MEDIAN_BLUR_SIZE = 5

# Software depth temporal smoothing
# Higher = smoother but more latency
# Good range: 0.45 to 0.70
DEPTH_SMOOTHING_ALPHA = 0.45

# =========================
# Despeckle filter
# =========================
# Removes isolated noisy pixels ("weird shapes") by comparing each
# pixel to a local blurred average and replacing outliers with that
# average, instead of a plain blur which would soften real terrain
# edges too. Runs on real millimetre height data, before both the
# colour map and contour lines are generated, so it cleans up both.
DESPECKLE_ENABLED = True

# Size of the local averaging window (must be odd; even values are
# automatically rounded up by 1).
DESPECKLE_BLUR_SIZE = 3

# How far a pixel can deviate from its local average (in mm) before
# being treated as noise and replaced. Lower = more aggressive
# cleanup (but risks smoothing out small real features). Higher =
# only removes obvious spikes.
DESPECKLE_THRESHOLD_MM = 1.5

# =========================
# Terrain smoothing
# =========================
# Lower blur = lower latency
BLUR_SIZE = 5

# Adaptive height smoothing in main.py
# When sand is moving, use less smoothing.
# When sand is still, use more smoothing.
HEIGHT_SMOOTHING_STILL_WEIGHT = 0.55
HEIGHT_SMOOTHING_MOVING_WEIGHT = 0.20
MOTION_THRESHOLD_MM = 12

# =========================
# Height-to-colour range
# =========================
# How far the sand can realistically be dug down / mounded up from the
# calibrated baseline, in millimetres. This is the single source of
# truth for the colour mapping range (water <-> land) — it's used both
# to clip sensor noise and to scale the colour gradient in main.py.
# Tune this to match your sandbox's actual usable sand depth: if the
# colours barely change while sculpting, this range is too wide for
# how much height variation your sand can physically produce.
#
# Note: contour line spacing (below) is independent of this range —
# changing this won't affect how close together contour lines appear.
MIN_WATER_HEIGHT_MM = -20
MAX_LAND_HEIGHT_MM = 20

# Controls how quickly raised terrain (land side, height >= 0) shifts
# from grass to mountain colours as it gets taller. Given as fractions
# of MAX_LAND_HEIGHT_MM (must start at 0.0, end at 1.0) paired with the
# corresponding 0-255 colour-scale value from terrain_processing.py's
# colour bands (105-120 = grass, 155 = darker hill, 175 = mountain/rock,
# 205+ = high mountain).
#
# The default below keeps most of the height range in the grass/hill
# zone, and only pushes into mountain colours near the very top —
# raise the middle fraction/value pairs to make more of the range grass,
# lower them to reach mountain colours sooner.
LAND_COLOR_HEIGHT_FRACTIONS = [0.0, 0.6, 0.95, 1.0]
LAND_COLOR_VALUES = [105, 125, 135, 185]

# =========================
# Contour settings
# =========================
SHOW_BASE_CONTOURS = False
SHOW_CHANGE_CONTOURS = True

BASE_CONTOUR_INTERVAL_MM = 10
BASE_CONTOUR_OFFSET_MM = 0

# Vertical spacing between contour lines, in real millimetres of sand
# height. This is independent of MIN_WATER_HEIGHT_MM/MAX_LAND_HEIGHT_MM
# above — it always means actual mm, regardless of the colour range.
# Lower = more, closer-together lines (more detail, but can look noisy
# on gentle slopes). Higher = fewer, more widely spaced lines.
# For a sandbox with ~40mm of usable height, 6-8mm is a reasonable
# starting point.
CONTOUR_INTERVAL_MM = 10

# Contour lines will never appear closer together than this, in mm,
# regardless of how small CONTOUR_INTERVAL_MM is set. Prevents overly
# dense/noisy lines on very steep slopes.
CONTOUR_MIN_INTERVAL_MM = 6

CONTOUR_MIN_AREA = 80

# Contour line thickness in pixels
# 1 = thinnest, 2 = medium, 3+ = thick
CONTOUR_LINE_THICKNESS = 1

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
PROJECTOR_WIDTH = 1024
PROJECTOR_HEIGHT = 768

# If projector is extended to the right of laptop screen,
# this is usually your laptop screen width.
PROJECTOR_X = 1920
PROJECTOR_Y = 0

# False = show on laptop/main screen
# True = move window to projector position
PROJECTOR_ON_SECOND_SCREEN = False

# =========================
# Projector physical size calibration
# =========================
# Measured size (cm) of the FULL projector output (PROJECTOR_WIDTH x
# PROJECTOR_HEIGHT pixels, no scaling/offset applied) at its current
# distance/zoom from the sandbox. Re-measure and update these if the
# projector's position, height, or zoom ever changes.
PROJECTOR_MEASURED_FULL_WIDTH_CM = 77.0
PROJECTOR_MEASURED_FULL_HEIGHT_CM = 57.5

# Target physical size of the projected image, in cm.
# This is the single source of truth for content size — there is no
# separate scale multiplier layered on top, so this number always
# reflects what's actually projected.
PROJECTOR_CONTENT_WIDTH_CM = 48.62
PROJECTOR_CONTENT_HEIGHT_CM = 42.25

# Position of the projected content's top-left corner, measured in cm
# from the top-left corner of the FULL projector output. This is the
# single source of truth for position — there is no separate pixel
# fine-tune offset layered on top.
PROJECTOR_CONTENT_OFFSET_TOP_CM = 11.75
PROJECTOR_CONTENT_OFFSET_LEFT_CM = 7.44