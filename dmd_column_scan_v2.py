"""
DMD Column Scan Script - Version 2
Uses 64-bit Python for camera and matplotlib
Communicates with 32-bit DMD server via files

Box region:
  Top-left: (row=364, col=324)
  Bottom-right: (row=420, col=436)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime
import os
import sys
import subprocess
import time

# Add Basler camera path
sys.path.append(r'C:\Users\srtwe\Box\EndresLab\z_Second Experiment\Code\Holoeye_SLM\camera_feedback')

from basler_camera import BaslerCamera

# Constants
ROW_WIDTH = 1024
NUM_ROWS = 768

# Box region definition
BOX_TOP_LEFT = (364, 344)      # (row, col)
BOX_BOTTOM_RIGHT = (420, 446)  # (row, col)

# Camera settings
EXPOSURE_TIME_US = 50    # Reduced to avoid saturation (was 5000)
NUM_AVERAGE = 3          # Number of images to average

# DMD server communication files
COMMAND_FILE = "dmd_command.txt"
PATTERN_FILE = "dmd_pattern.npy"
STATUS_FILE = "dmd_status.txt"

# Path to 32-bit Python
PYTHON_32BIT = r"./venv_32bit/Scripts/python.exe"


class DMDClient:
    """Client to communicate with DMD server running on 32-bit Python"""

    def __init__(self):
        self.server_process = None

    def start_server(self):
        """Start the DMD server in a subprocess"""
        print("[DMD CLIENT] Starting DMD server (32-bit Python)...")

        # Clean up old communication files
        for f in [COMMAND_FILE, STATUS_FILE]:
            if os.path.exists(f):
                os.remove(f)

        # Start server
        self.server_process = subprocess.Popen(
            [PYTHON_32BIT, "dmd_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Wait for server to be ready
        print("[DMD CLIENT] Waiting for DMD server to initialize...")
        timeout = 30
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    status = f.read().strip()
                if status == "READY":
                    print("[DMD CLIENT] DMD server is ready")
                    return
            time.sleep(0.1)

        raise RuntimeError("DMD server failed to start within timeout")

    def send_pattern(self, pattern):
        """Send pattern to DMD server"""
        # Save pattern to file
        np.save(PATTERN_FILE, pattern)

        # Send command
        with open(COMMAND_FILE, 'w') as f:
            f.write("SEND_PATTERN")

        # Wait for completion
        timeout = 5
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    status = f.read().strip()
                if status == "READY":
                    return
            time.sleep(0.01)

        raise RuntimeError("DMD server failed to respond")

    def stop_server(self):
        """Stop the DMD server"""
        print("[DMD CLIENT] Stopping DMD server...")

        # Send quit command
        with open(COMMAND_FILE, 'w') as f:
            f.write("QUIT")

        # Wait for server to stop
        if self.server_process:
            self.server_process.wait(timeout=5)
            print("[DMD CLIENT] DMD server stopped")

        # Clean up communication files
        for f in [COMMAND_FILE, PATTERN_FILE, STATUS_FILE]:
            if os.path.exists(f):
                os.remove(f)


def create_pattern_with_columns_off(max_column_off):
    """
    Create DMD pattern with columns 0 to max_column_off turned off in the box region.
    Everything outside the box is off. Inside the box, columns 0 to max_column_off are off,
    remaining columns are on.

    Args:
        max_column_off: Maximum column index (in box coordinates) to turn off (inclusive).
                       All columns from 0 to max_column_off will be off.
                       If -1, all columns are on.

    Returns:
        pixel_array: 768x1024 numpy array (0=off/white, 1=on/black)
    """
    # Start with all pixels off (0)
    pixel_array = np.zeros((NUM_ROWS, ROW_WIDTH), dtype=np.uint8)

    # Extract box coordinates
    row_start, col_start = BOX_TOP_LEFT
    row_end, col_end = BOX_BOTTOM_RIGHT

    # Turn on all pixels in the box (set to 1 = on/black)
    pixel_array[row_start:row_end+1, col_start:col_end+1] = 1

    # Turn off columns 0 to max_column_off (cumulative)
    if max_column_off >= 0:
        for col_offset in range(max_column_off + 1):
            actual_col = col_start + col_offset
            if col_start <= actual_col <= col_end:
                pixel_array[row_start:row_end+1, actual_col] = 0  # Off (white)

    return pixel_array


def visualize_dmd_pattern(pixel_array, max_column_off):
    """Create visualization of DMD pattern focused on the box region"""
    row_start, col_start = BOX_TOP_LEFT
    row_end, col_end = BOX_BOTTOM_RIGHT

    # Extract box region for visualization
    box_region = pixel_array[row_start:row_end+1, col_start:col_end+1]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Display box region (invert colors: 0=off=white, 1=on=black)
    display_array = np.where(box_region == 0, 255, 0).astype(np.uint8)

    im = ax.imshow(display_array, cmap='gray', vmin=0, vmax=255,
                   interpolation='nearest', aspect='auto')

    # Add grid lines for columns
    box_width = col_end - col_start + 1
    ax.set_xticks(np.arange(0, box_width, 10))
    ax.set_yticks(np.arange(0, row_end - row_start + 1, 10))
    ax.grid(True, alpha=0.3, linewidth=0.5)

    # Labels
    ax.set_xlabel('Column Index (relative to box)', fontweight='bold')
    ax.set_ylabel('Row Index (relative to box)', fontweight='bold')

    title = f'DMD Pattern - Box Region\n'
    if max_column_off < 0:
        title += 'All columns ON'
    else:
        title += f'Columns 0-{max_column_off} OFF'
    ax.set_title(title, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Pixel State (White=Off, Black=On)', fontweight='bold')

    plt.tight_layout()
    return fig


def create_combined_plots(camera_images, column_configs, save_dir, global_vmin, global_vmax):
    """Create combined plots showing DMD config and camera image side by side"""
    num_configs = len(camera_images)

    for idx in range(num_configs):
        fig = plt.figure(figsize=(14, 6))
        gs = GridSpec(1, 2, figure=fig, width_ratios=[1, 1])

        # DMD pattern visualization
        ax1 = fig.add_subplot(gs[0])
        pattern = create_pattern_with_columns_off(column_configs[idx])
        row_start, col_start = BOX_TOP_LEFT
        row_end, col_end = BOX_BOTTOM_RIGHT
        box_region = pattern[row_start:row_end+1, col_start:col_end+1]
        display_array = np.where(box_region == 0, 255, 0).astype(np.uint8)

        im1 = ax1.imshow(display_array, cmap='gray', vmin=0, vmax=255,
                        interpolation='nearest', aspect='auto')
        ax1.set_xlabel('Column Index (relative to box)', fontweight='bold')
        ax1.set_ylabel('Row Index (relative to box)', fontweight='bold')

        if column_configs[idx] < 0:
            ax1.set_title('DMD Pattern\nAll columns ON', fontweight='bold')
        else:
            ax1.set_title(f'DMD Pattern\nColumns 0-{column_configs[idx]} OFF', fontweight='bold')

        plt.colorbar(im1, ax=ax1, label='Pixel State')

        # Camera image - zoomed into center by factor of 4
        ax2 = fig.add_subplot(gs[1])
        camera_img = camera_images[idx]

        # Zoom into center by factor of 4
        h, w = camera_img.shape
        center_y, center_x = h // 2, w // 2
        crop_h, crop_w = h // 4, w // 4

        y_start = center_y - crop_h // 2
        y_end = center_y + crop_h // 2
        x_start = center_x - crop_w // 2
        x_end = center_x + crop_w // 2

        camera_img_zoomed = camera_img[y_start:y_end, x_start:x_end]

        im2 = ax2.imshow(camera_img_zoomed, cmap='hot', vmin=global_vmin, vmax=global_vmax, interpolation='nearest')
        ax2.set_xlabel('X (pixels)', fontweight='bold')
        ax2.set_ylabel('Y (pixels)', fontweight='bold')
        ax2.set_title(f'Camera Image (4x zoom, center)\nMax: {np.max(camera_img_zoomed):.1f}', fontweight='bold')
        plt.colorbar(im2, ax=ax2, label='Intensity')

        # Overall title
        fig.suptitle(f'Configuration {idx}: DMD Pattern and Camera Response',
                    fontsize=14, fontweight='bold', y=0.98)

        plt.tight_layout()

        # Save
        filename = os.path.join(save_dir, f"combined_config_{idx:03d}.png")
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  Saved: combined_config_{idx:03d}.png")
        plt.close(fig)


def run_column_scan(step=10):
    """Run the column scan experiment"""
    # Create results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"dmd_column_scan_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    print(f"\n[INFO] Results will be saved to: {results_dir}/")

    # Calculate box dimensions
    row_start, col_start = BOX_TOP_LEFT
    row_end, col_end = BOX_BOTTOM_RIGHT
    box_width = col_end - col_start + 1
    box_height = row_end - row_start + 1

    print(f"\n[INFO] Box region:")
    print(f"  Top-left: (row={row_start}, col={col_start})")
    print(f"  Bottom-right: (row={row_end}, col={col_end})")
    print(f"  Dimensions: {box_width} cols x {box_height} rows")
    print(f"  Scanning every {step} columns")

    # Initialize DMD client and server
    dmd_client = DMDClient()
    dmd_client.start_server()

    # Initialize camera
    print(f"\n[INFO] Initializing camera...")
    camera = BaslerCamera(exposure_time_us=EXPOSURE_TIME_US)

    # Generate column configurations to test
    column_configs = []

    # Configuration 0: All columns on (max_column_off = -1)
    column_configs.append(-1)

    # Configurations 1-N: Turn off columns 0 to N progressively
    for col_idx in range(0, box_width, step):
        column_configs.append(col_idx)

    print(f"\n[INFO] Testing {len(column_configs)} configurations")

    # Storage for results
    all_camera_images = []

    # Global colorbar limits (set from first image)
    global_vmin = None
    global_vmax = None

    try:
        for config_idx, max_column_off in enumerate(column_configs):
            print(f"\n[INFO] Configuration {config_idx}/{len(column_configs)-1}:")
            if max_column_off < 0:
                print(f"  Columns off: None (all on)")
            else:
                print(f"  Columns off: 0 to {max_column_off}")

            # Create DMD pattern
            pattern = create_pattern_with_columns_off(max_column_off)

            # Send to DMD via server
            dmd_client.send_pattern(pattern)
            print(f"  Pattern sent to DMD")

            # Wait a bit for DMD to settle
            time.sleep(0.2)

            # Capture camera image
            camera_image = camera.capture_image(num_average=NUM_AVERAGE)
            print(f"  Camera image captured: {camera_image.shape}, max={np.max(camera_image):.1f}")

            # Set global colorbar limits from first image
            if config_idx == 0:
                global_vmin = np.min(camera_image)
                global_vmax = np.max(camera_image)
                print(f"  Setting global colorbar limits: min={global_vmin:.1f}, max={global_vmax:.1f}")

            # Check saturation
            is_sat, max_val, sat_frac = camera.check_saturation(camera_image)
            if is_sat:
                print(f"  WARNING: Camera saturated! ({sat_frac*100:.2f}% pixels)")

            # Store results
            all_camera_images.append(camera_image)

            # Save individual files
            config_name = f"config_{config_idx:03d}"

            # Save camera image as numpy
            np.save(os.path.join(results_dir, f"{config_name}_camera.npy"), camera_image)

            # Save DMD pattern as numpy
            np.save(os.path.join(results_dir, f"{config_name}_dmd_pattern.npy"), pattern)

            # Save DMD pattern visualization as PNG
            dmd_fig = visualize_dmd_pattern(pattern, max_column_off)
            dmd_fig.savefig(os.path.join(results_dir, f"{config_name}_dmd_pattern.png"),
                           dpi=150, bbox_inches='tight')
            plt.close(dmd_fig)

            # Save camera image as PNG (with consistent colorbar)
            plt.figure(figsize=(8, 6))
            plt.imshow(camera_image, cmap='hot', vmin=global_vmin, vmax=global_vmax, interpolation='nearest')
            plt.colorbar(label='Intensity')
            plt.title(f'Camera Image - Config {config_idx}\nMax: {np.max(camera_image):.1f}')
            plt.xlabel('X (pixels)')
            plt.ylabel('Y (pixels)')
            plt.tight_layout()
            plt.savefig(os.path.join(results_dir, f"{config_name}_camera.png"),
                       dpi=150, bbox_inches='tight')
            plt.close()

        print(f"\n[INFO] All configurations tested. Creating combined plots...")

        # Create combined plots (with consistent colorbar)
        create_combined_plots(all_camera_images, column_configs, results_dir, global_vmin, global_vmax)

        print(f"\n[INFO] Experiment complete!")
        print(f"[INFO] Results saved to: {results_dir}/")

    finally:
        # Cleanup
        camera.close()
        print("[INFO] Camera closed")

        dmd_client.stop_server()


if __name__ == "__main__":
    print("="*60)
    print("DMD Column Scan Experiment (Version 2)")
    print("="*60)

    # Run with step size of 10 columns
    run_column_scan(step=10)
