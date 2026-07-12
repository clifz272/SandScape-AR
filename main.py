# main.py

import cv2
import numpy as np

from camera import DepthCamera
from calibration import SandboxCalibrator

from terrain_processing import (
    smooth_depth_map,
    create_height_colormap
)

from contour_generator import (
    generate_contour_overlay_from_height_change,
    generate_base_contours_from_depth
)

from projection_mapper import (
    resize_for_projector,
    show_projection,
    close_projection
)

from config import (
    DEBUG_WINDOWS,
    HEIGHT_SMOOTHING_STILL_WEIGHT,
    HEIGHT_SMOOTHING_MOVING_WEIGHT,
    MOTION_THRESHOLD_MM,
    SHOW_BASE_CONTOURS,
    SHOW_CHANGE_CONTOURS,
    PROJECTOR_ON_SECOND_SCREEN,
    PROCESSING_SCALE
)


def create_control_panel():
    """
    Create the control panel image once.
    This avoids redrawing text every frame.
    """

    control_panel = np.zeros((120, 400, 3), dtype=np.uint8)

    cv2.putText(
        control_panel,
        "AR Sandbox Controls",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        control_panel,
        "Press C = Recalibrate",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1
    )

    cv2.putText(
        control_panel,
        "Press Q / ESC = Quit",
        (20, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1
    )

    return control_panel


def main():
    print("Starting AR Sandbox Prototype...")
    print("Press 'q' to quit.")
    print("Press 'c' to recalibrate.")

    camera = DepthCamera()
    calibrator = SandboxCalibrator()

    stable_height_change = None
    frame_count = 0

    try:
        calibrator.calibrate(camera)

        cv2.namedWindow("Controls", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Controls", 400, 120)
        cv2.moveWindow("Controls", 50, 50)

        control_panel = create_control_panel()

        while True:
            original_frame, depth_mm, height_map = camera.get_depth_frame()

            # Crop to selected sandbox area
            sandbox_depth_mm = calibrator.crop_to_sandbox(depth_mm)
            sandbox_color_view = calibrator.crop_to_sandbox(original_frame)

            # Height difference from calibration baseline
            height_change_mm = calibrator.get_height_change_map(depth_mm)

            if height_change_mm is None:
                key = cv2.waitKey(1) & 0xFF
                if key in [ord('q'), ord('Q'), 27]:
                    break
                continue

            height_change_mm = height_change_mm.astype(np.float32)

            # =========================
            # Adaptive smoothing
            # =========================
            # When movement is high:
            #   use low smoothing for fast response.
            # When movement is low:
            #   use higher smoothing for stable image.
            if stable_height_change is None:
                stable_height_change = height_change_mm.copy()
            else:
                motion_amount = np.mean(
                    np.abs(height_change_mm - stable_height_change)
                )

                if motion_amount > MOTION_THRESHOLD_MM:
                    smoothing_weight = HEIGHT_SMOOTHING_MOVING_WEIGHT
                else:
                    smoothing_weight = HEIGHT_SMOOTHING_STILL_WEIGHT

                stable_height_change = (
                    smoothing_weight * stable_height_change
                    + (1.0 - smoothing_weight) * height_change_mm
                )

            height_change_mm = stable_height_change.copy()

            # Remove tiny flicker around calibrated base level
            height_change_mm[np.abs(height_change_mm) < 5] = 0

            # Remove extreme sensor noise
            height_change_mm = np.clip(height_change_mm, -60, 80)
            
            # =========================
            # Raspberry Pi performance:
            # process smaller image, then resize final output later
            # =========================
            if PROCESSING_SCALE < 1.0:
                h, w = height_change_mm.shape[:2]

                process_w = max(1, int(w * PROCESSING_SCALE))
                process_h = max(1, int(h * PROCESSING_SCALE))

                height_change_mm = cv2.resize(
                    height_change_mm,
                    (process_w, process_h),
                    interpolation=cv2.INTER_AREA
                )

                sandbox_depth_mm = cv2.resize(
                    sandbox_depth_mm,
                    (process_w, process_h),
                    interpolation=cv2.INTER_AREA
                )

            # =========================
            # Better height-to-colour mapping
            # =========================
            # Negative = dug down / water
            # 0 mm = normal calibrated sand level / grass
            # Positive = raised terrain / mountain

            MIN_WATER_HEIGHT_MM = -60
            MAX_LAND_HEIGHT_MM = 80

            height_for_colour = np.clip(
                height_change_mm,
                MIN_WATER_HEIGHT_MM,
                MAX_LAND_HEIGHT_MM
            )

            visual_height = np.zeros_like(height_for_colour, dtype=np.uint8)

            # Lower than baseline becomes water/coast
            negative_mask = height_for_colour < 0

            visual_height[negative_mask] = np.interp(
                height_for_colour[negative_mask],
                [MIN_WATER_HEIGHT_MM, 0],
                [20, 115]
            ).astype(np.uint8)

            # Baseline and raised terrain become grass/hill/mountain
            positive_mask = height_for_colour >= 0

            visual_height[positive_mask] = np.interp(
                height_for_colour[positive_mask],
                [0, MAX_LAND_HEIGHT_MM],
                [125, 240]
            ).astype(np.uint8)

            # =========================
            # Terrain colour updates every frame
            # =========================
            smoothed_depth = smooth_depth_map(visual_height)
            terrain_color = create_height_colormap(smoothed_depth)

            final_output = terrain_color.copy()

            # =========================
            # Optional base contour
            # =========================
            # Keep this OFF for low latency.
            if SHOW_BASE_CONTOURS:
                final_output = generate_base_contours_from_depth(
                    sandbox_depth_mm,
                    final_output
                )

            # =========================
            # Synced topography lines
            # =========================
            # Important:
            # Use smoothed_depth, not height_change_mm.
            # This makes contour lines follow the colour map exactly.
            # Also generate every frame because this contour method is lightweight.
            frame_count += 1

            if SHOW_CHANGE_CONTOURS:
                contour_overlay = generate_contour_overlay_from_height_change(
                    smoothed_depth,
                    final_output.shape
                )

                contour_mask = np.any(contour_overlay > 0, axis=2)
                final_output[contour_mask] = contour_overlay[contour_mask]

            # Resize for projector
            projector_output = resize_for_projector(final_output)

            # Show projection
            show_projection(
                projector_output,
                fullscreen=True,
                second_screen=PROJECTOR_ON_SECOND_SCREEN
            )

            # Debug windows only when needed
            if DEBUG_WINDOWS:
                change_mask = calibrator.detect_significant_changes(depth_mm)

                if change_mask is not None:
                    cv2.imshow("Height Change Detection", change_mask)

                cv2.imshow("Camera View", sandbox_color_view)
                cv2.imshow("Depth Map", smoothed_depth)

            # Control window
            if frame_count % 20 == 0:
                cv2.imshow("Controls", control_panel)   

            # Low waitKey value reduces display/input delay
            key = cv2.waitKey(1) & 0xFF

            if key in [ord('q'), ord('Q'), 27]:
                break

            if key in [ord('c'), ord('C')]:
                print("Recalibrating...")

                close_projection()
                cv2.waitKey(500)

                # Reset smoothing and cached contours
                stable_height_change = None
                frame_count = 0
                camera.previous_depth_mm = None

                calibrator.calibrate(camera)

                cv2.namedWindow("Controls", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Controls", 400, 120)
                cv2.moveWindow("Controls", 50, 50)

                control_panel = create_control_panel()

    except KeyboardInterrupt:
        print("Program stopped by user.")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("AR Sandbox stopped.")


if __name__ == "__main__":
    main()
