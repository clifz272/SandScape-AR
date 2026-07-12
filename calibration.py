# calibration.py

import cv2
import numpy as np

from config import (
    CALIBRATION_FRAMES,
    SANDBOX_MIN_VALID_MM,
    SANDBOX_MAX_VALID_MM,
    MIN_SANDBOX_AREA,
    HEIGHT_CHANGE_THRESHOLD_MM
)


class SandboxCalibrator:
    def __init__(self):
        self.roi = None
        self.baseline_depth_mm = None
        self.baseline_mean_depth = None

    def calibrate(self, camera):
        """
        Capture several frames at startup to detect sandbox region
        and store baseline sand depth.
        """
        print("Starting calibration...")
        print("Please keep the sandbox empty and do not move the sand.")

        depth_frames = []
        color_frame = None

        for i in range(CALIBRATION_FRAMES):
            color_frame, depth_mm, height_map = camera.get_depth_frame()
            depth_frames.append(depth_mm)

            preview = height_map.copy()
            cv2.putText(
                preview,
                f"Calibrating... {i + 1}/{CALIBRATION_FRAMES}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                255,
                2
            )

            cv2.imshow("Calibration Preview", preview)
            cv2.waitKey(1)

        cv2.destroyWindow("Calibration Preview")

        # Average depth to reduce noise
        avg_depth = np.mean(depth_frames, axis=0)

        # Let user manually select sandbox area
        preview = cv2.normalize(avg_depth, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")
        preview = cv2.applyColorMap(preview, cv2.COLORMAP_JET)

        print("Select the sandbox area, then press ENTER or SPACE.")
        print("Press C to cancel and use auto detection.")

        manual_roi = cv2.selectROI("Select Sandbox ROI", preview, False, False)
        cv2.destroyWindow("Select Sandbox ROI")

        x, y, w, h = manual_roi

        if w > 0 and h > 0:
            self.roi = (x, y, w, h)
            print("Using manual sandbox ROI.")
        else:
            self.roi = self.detect_sandbox_roi(avg_depth)
            print("Using automatic sandbox ROI.")
        x, y, w, h = self.roi

        self.baseline_depth_mm = avg_depth[y:y+h, x:x+w].copy()
        self.baseline_mean_depth = float(np.mean(self.baseline_depth_mm))

        print("Calibration complete.")
        print(f"Sandbox ROI: x={x}, y={y}, width={w}, height={h}")
        print(f"Baseline mean depth: {self.baseline_mean_depth:.2f} mm")

        return self.roi

    def detect_sandbox_roi(self, depth_mm):
        """
        Detect sandbox area using valid depth range.
        """
        valid_mask = (
            (depth_mm > SANDBOX_MIN_VALID_MM) &
            (depth_mm < SANDBOX_MAX_VALID_MM)
        ).astype(np.uint8) * 255

        kernel = np.ones((7, 7), np.uint8)
        valid_mask = cv2.morphologyEx(valid_mask, cv2.MORPH_CLOSE, kernel)
        valid_mask = cv2.morphologyEx(valid_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            valid_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            print("Warning: Could not detect sandbox. Using full camera frame.")
            h, w = depth_mm.shape
            return (0, 0, w, h)

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area < MIN_SANDBOX_AREA:
            print("Warning: Detected sandbox area too small. Using full frame.")
            h, w = depth_mm.shape
            return (0, 0, w, h)

        x, y, w, h = cv2.boundingRect(largest)
        return (x, y, w, h)

    def crop_to_sandbox(self, image):
        """
        Crop image to calibrated sandbox region.
        """
        if self.roi is None:
            return image

        x, y, w, h = self.roi
        return image[y:y+h, x:x+w]

    def get_height_change_map(self, current_depth_mm):
        """
        Compare current depth against baseline depth.
        Includes sensor-shake compensation using median global depth shift.
        """

        if self.roi is None or self.baseline_depth_mm is None:
            return None

        x, y, w, h = self.roi

        current_crop = current_depth_mm[y:y+h, x:x+w].astype("float32")
        baseline = self.baseline_depth_mm.astype("float32")

        # Raw height change:
        # positive = object/sand is closer/higher than baseline
        raw_change = baseline - current_crop

        # Estimate global sensor shake / vibration offset
        # If the whole image shifted by a few mm, median catches it
        global_shift = np.median(raw_change)

        # Remove global shift caused by sensor movement
        stable_change = raw_change - global_shift

        # Ignore tiny noise/flicker
        stable_change[np.abs(stable_change) < 6] = 0

        return stable_change

    def detect_significant_changes(self, current_depth_mm):
        """
        Detect where sand height has changed compared to startup baseline.
        """
        height_change = self.get_height_change_map(current_depth_mm)

        if height_change is None:
            return None

        change_mask = np.abs(height_change) > HEIGHT_CHANGE_THRESHOLD_MM

        return change_mask.astype(np.uint8) * 255