# camera.py
# Raspberry Pi ultra low-latency depth-only RealSense version

import cv2
import numpy as np
import pyrealsense2 as rs

from config import (
    MIN_DEPTH_MM,
    MAX_DEPTH_MM,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_FPS,
    DEPTH_SMOOTHING_ALPHA,
    MEDIAN_BLUR_SIZE
)


class DepthCamera:
    def __init__(self):
        print("Using Intel RealSense D435i/D435 depth-only mode")

        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Depth only = lower USB bandwidth and lower CPU load
        self.config.enable_stream(
            rs.stream.depth,
            CAMERA_WIDTH,
            CAMERA_HEIGHT,
            rs.format.z16,
            CAMERA_FPS
        )

        self.profile = self.pipeline.start(self.config)

        depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        print("Depth scale:", self.depth_scale)

        self.previous_depth_mm = None

    def get_depth_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        if not depth_frame:
            raise RuntimeError("Failed to get RealSense depth frame.")

        depth_raw = np.asanyarray(depth_frame.get_data())

        depth_mm = depth_raw.astype(np.float32) * self.depth_scale * 1000.0

        # Invalid RealSense pixels are usually 0.
        # Do NOT turn them into MAX_DEPTH_MM immediately,
        # because that creates fake dark-blue water around edges.
        invalid_mask = depth_mm <= 0

        if np.any(invalid_mask):
            if self.previous_depth_mm is not None:
                # Use previous valid depth for bad pixels
                depth_mm[invalid_mask] = self.previous_depth_mm[invalid_mask]
            else:
                # First frame: use median of valid depth pixels
                valid_pixels = depth_mm[~invalid_mask]

                if valid_pixels.size > 0:
                    median_depth = np.median(valid_pixels)
                    depth_mm[invalid_mask] = median_depth
                else:
                    depth_mm[invalid_mask] = MAX_DEPTH_MM

        # Keep useful sandbox range
        depth_mm = np.clip(depth_mm, MIN_DEPTH_MM, MAX_DEPTH_MM)

        # Very light median blur
        median_size = MEDIAN_BLUR_SIZE

        if median_size % 2 == 0:
            median_size += 1

        if median_size >= 3:
            depth_mm = cv2.medianBlur(
                depth_mm.astype(np.float32),
                median_size
            )

        # Very light temporal smoothing
        if self.previous_depth_mm is None:
            stable_depth_mm = depth_mm
        else:
            stable_depth_mm = (
                DEPTH_SMOOTHING_ALPHA * self.previous_depth_mm
                + (1.0 - DEPTH_SMOOTHING_ALPHA) * depth_mm
            )

        self.previous_depth_mm = stable_depth_mm.copy()

        height_map = self.convert_depth_to_heightmap(stable_depth_mm)

        # Fake colour frame for compatibility with your main.py/calibration.py
        color_image = cv2.cvtColor(height_map, cv2.COLOR_GRAY2BGR)

        return color_image, stable_depth_mm, height_map

    def convert_depth_to_heightmap(self, depth_mm):
        height_map = (MAX_DEPTH_MM - depth_mm) / (MAX_DEPTH_MM - MIN_DEPTH_MM)
        height_map = height_map * 255.0
        height_map = np.clip(height_map, 0, 255)

        return height_map.astype(np.uint8)

    def release(self):
        self.pipeline.stop()
