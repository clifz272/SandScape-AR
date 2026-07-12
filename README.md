# CEG1010 Group 4 — Augmented Reality Sandbox

An augmented reality sandbox built for the Raspberry Pi using an Intel RealSense D435 / D435i depth camera. The system scans the sand, calibrates a baseline, and projects a live, colour-coded topography map (with contour lines and water effects) directly onto the sand as it is shaped.

## Hardware Requirements

- Intel RealSense D435 or D435i depth camera
- Raspberry Pi (or other Linux machine) with a free USB 3.0 port
- Projector, mounted above the sandbox and aligned to the sand surface
- A sandbox filled with sand

## Software Requirements

- Python 3.13 (aarch64 / Linux — a prebuilt `pyrealsense2` binary for this exact platform is included)
- OpenCV and NumPy (see `requirements.txt`)
- `librealsense` core SDK installed on the system (not included in this repo) — see [realsenseai/librealsense](https://github.com/realsenseai/librealsense)

## Installation

1. **Install system dependencies** (Raspberry Pi OS / Debian-based):
   ```bash
   sudo apt update
   sudo apt install python3-pip libusb-1.0-0-dev
   ```

2. **(Optional) Create a virtual environment.** Keeps project dependencies isolated from the system Python:
```bash
   python3 -m venv venv
   source venv/bin/activate
```
   You'll need to run `source venv/bin/activate` again in any new terminal session before running the project. If you skip this step, dependencies install to the system Python instead.

3. **Install the `librealsense` core SDK.** This provides the `librealsense2` shared libraries that the bundled `pyrealsense2` binding depends on at runtime:
```bash
   git clone https://github.com/realsenseai/librealsense.git
   cd librealsense
   mkdir build && cd build
   cmake ..
   cmake --build .
   sudo cmake --install .
```
   Follow the official [Raspberry Pi guide](https://dev.realsenseai.com/docs/using-depth-camera-with-raspberry-pi-3) or [Linux guide](https://github.com/realsenseai/librealsense/blob/master/doc/installation.md) for platform-specific dependencies and build flags. This step can take a while on a Pi — the `-j` flag on `cmake --build . -- -j$(nproc)` speeds it up if you have enough RAM/swap.
 
   Verify the install:
```bash
   ldconfig -p | grep realsense
```
   This should list `librealsense2.so`. If it returns nothing, the SDK isn't installed or isn't on the linker path yet.

4. **Install the RealSense udev rules.** This is required for the camera to be accessible without root privileges:
   ```bash
   sudo cp 99-realsense-libusb.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```
   Unplug and replug the camera after this step.

5. **Install the `pyrealsense2` Python bindings.**
   This repo includes a prebuilt binary for Python 3.13 on aarch64 Linux (`pyrealsense2.cpython-313-aarch64-linux-gnu.so`):
   ```bash
   SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
   cp pyrealsense2.cpython-313-aarch64-linux-gnu.so "$SITE_PACKAGES/"
   ```
   Verify it's importable:
   ```bash
   python3 -c "import pyrealsense2 as rs; print(rs.__file__)"
   ```
   If this fails, your interpreter's ABI tag may not match the prebuilt binary (check with `python3 -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"` — it should read `.cpython-313-aarch64-linux-gnu.so`). It can also fail if the core SDK from step 3 isn't installed. As a last resort, install `pyrealsense2` normally instead:
   ```bash
   pip install pyrealsense2
   ```

6. **Install the remaining Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

7. **Verify the camera is working:**
   ```bash
   python3 test_realsense.py
   ```
   This should open two windows showing the live colour and depth feeds. Press `q` to quit.

## Usage

Run the main application:

```bash
python3 main.py
```

- On startup, the sandbox is calibrated: keep the sand still and empty while the camera captures frames.
- A preview window appears — either drag a box around the sandbox area and press **Enter/Space**, or press **C** to fall back to automatic detection.
- Once calibrated, the terrain map is projected live. Sculpt the sand and watch the colours and contour lines update in real time.

### Controls

| Key | Action |
|-----|--------|
| `C` | Recalibrate the sandbox baseline |
| `Q` / `Esc` | Quit the application |


## Configuration
 
All tunable parameters live in `config.py`, grouped by section:
 
- **Depth range** (`MIN_DEPTH_MM`, `MAX_DEPTH_MM`) — the usable depth window in millimetres.
- **Camera** (`CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`, `PROCESSING_SCALE`) — resolution, frame rate, and the internal processing scale used to keep the Pi responsive.
- **Software depth filtering** (`MEDIAN_BLUR_SIZE`, `DEPTH_SMOOTHING_ALPHA`) — noise reduction and temporal smoothing applied to the raw depth stream.
- **Terrain smoothing** — `BLUR_SIZE` for the displayed height map, plus adaptive smoothing (`HEIGHT_SMOOTHING_STILL_WEIGHT`, `HEIGHT_SMOOTHING_MOVING_WEIGHT`, `MOTION_THRESHOLD_MM`) that reacts differently depending on whether the sand is being actively moved.
- **Contours** — interval spacing (`CONTOUR_INTERVAL_MM`), line thickness (`CONTOUR_LINE_THICKNESS`), and whether base/change contours are shown (`SHOW_BASE_CONTOURS`, `SHOW_CHANGE_CONTOURS`).
- **Calibration** — number of frames used to establish the baseline, valid depth range for auto sandbox detection, and the height-change threshold considered "significant."
- **Projector** — output resolution and window position (`PROJECTOR_X`/`PROJECTOR_Y`), and whether to launch on a second screen.
If the projected image is laggy, try lowering `PROCESSING_SCALE`, `CAMERA_FPS`, or `CONTOUR_INTERVAL_MM` (a higher interval value means fewer, faster contour lines).
 
## Troubleshooting
 
- **Camera not detected / permission denied:** Make sure the udev rule is installed (see Installation step 2) and the camera has been unplugged/replugged since.
- **`ImportError: No module named pyrealsense2`:** The bundled `.so` file only works for Python 3.13 on aarch64 Linux. On any other setup, install `pyrealsense2` via pip instead.
- **`ImportError`/`undefined symbol` when importing `pyrealsense2` even on the right platform:** The core `librealsense2` SDK (step 3 above) is likely missing or not on the linker path. Run `sudo ldconfig` after installing it, and check with `ldconfig -p | grep realsense`.
- **Noisy or flickering depth image:** Increase `DEPTH_SMOOTHING_ALPHA` or `MEDIAN_BLUR_SIZE` in `config.py`.
- **Projector output on the wrong screen:** Adjust `PROJECTOR_X`/`PROJECTOR_Y` and set `PROJECTOR_ON_SECOND_SCREEN = True` in `config.py`.