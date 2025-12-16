"""
DMD Column Scan Script
Systematically turns off columns in a defined box region on the DMD
and captures camera images for each configuration.

Box region:
  Top-left: (row=364, col=324)
  Bottom-right: (row=420, col=436)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import ctypes
from datetime import datetime
import os
import sys

# Add Basler camera path
sys.path.append(r'C:\Users\srtwe\Box\EndresLab\z_Second Experiment\Code\Holoeye_SLM\camera_feedback')

from dmd_dll_class import DMD, create_bit_packed_row
from basler_camera import BaslerCamera

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

# Box region definition
BOX_TOP_LEFT = (364, 324)      # (row, col)
BOX_BOTTOM_RIGHT = (420, 436)  # (row, col)

# Camera settings
EXPOSURE_TIME_US = 5000  # Adjust as needed
NUM_AVERAGE = 3          # Number of images to average


def initialize_dmd():
    """Initialize the DMD"""
    print("[INFO] Initializing DMD...")
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER,
              row_width=ROW_WIDTH, num_rows=NUM_ROWS)
    dmd.reset_clear_old()
    print("[INFO] DMD initialized")
    return dmd


def create_pattern_with_columns_off(columns_off_list):
    """
    Create DMD pattern with specified columns turned off in the box region.
    Everything outside the box is off. Inside the box, all columns are on except
    those in columns_off_list.

    Args:
        columns_off_list: List of column indices (in box coordinates) to turn off

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

    # Turn off specified columns in the box
    for col_offset in columns_off_list:
        actual_col = col_start + col_offset
        if col_start <= actual_col <= col_end:
            pixel_array[row_start:row_end+1, actual_col] = 0  # Off (white)

    return pixel_array


def send_pattern_to_dmd(dmd, pixel_array):
    """
    Send pattern to DMD using the working 2-batch method

    Args:
        dmd: DMD object
        pixel_array: 768x1024 numpy array
    """
    # Reset DMD to start position - CRITICAL!
    dmd.reset_clear_old()

    # BATCH 1: Top half (rows 0-383)
    BATCH_ROWS = NUM_ROWS // 2
    batch1 = bytearray()
    for row_idx in range(0, BATCH_ROWS):
        pixel_row = pixel_array[row_idx, :].tolist()
        row_data = create_bit_packed_row(pixel_row, row_width=ROW_WIDTH)
        batch1.extend(row_data)

    batch1_array = (ctypes.c_ubyte * len(batch1))(*batch1)
    dmd.load_row(batch1_array)
    dmd.load_control()

    # BATCH 2: Bottom half (rows 384-767)
    batch2 = bytearray()
    for row_idx in range(BATCH_ROWS, NUM_ROWS):
        pixel_row = pixel_array[row_idx, :].tolist()
        row_data = create_bit_packed_row(pixel_row, row_width=ROW_WIDTH)
        batch2.extend(row_data)

    batch2_array = (ctypes.c_ubyte * len(batch2))(*batch2)
    dmd.load_row(batch2_array)

    # Display
    dmd.reset_clear()


def visualize_dmd_pattern(pixel_array, columns_off_list):
    """
    Create visualization of DMD pattern focused on the box region

    Args:
        pixel_array: Full DMD pattern
        columns_off_list: List of columns that are off

    Returns:
        fig: Matplotlib figure
    """
    row_start, col_start = BOX_TOP_LEFT
    row_end, col_end = BOX_BOTTOM_RIGHT

    # Extract box region for visualization
    box_region = pixel_array[row_start:row_end+1, col_start:col_end+1]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Display box region (invert colors: 0=off=white, 1=on=black)
    # For display, we want off=white (255) and on=black (0)
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
    if len(columns_off_list) == 0:
        title += 'All columns ON'
    else:
        title += f'Columns OFF: {columns_off_list}'
    ax.set_title(title, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Pixel State (White=Off, Black=On)', fontweight='bold')

    plt.tight_layout()
    return fig


def run_column_scan(step=10):
    """
    Run the column scan experiment

    Args:
        step: Column step size (every Nth column)
    """
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

    # Initialize DMD
    dmd = initialize_dmd()

    # Initialize camera
    print(f"\n[INFO] Initializing camera...")
    camera = BaslerCamera(exposure_time_us=EXPOSURE_TIME_US)

    # Generate column configurations to test
    # Start with all columns on, then turn off columns progressively
    column_configs = []

    # Configuration 0: All columns on
    column_configs.append([])

    # Configurations 1-N: Turn off columns 0, 10, 20, ..., 0+10, 0+20, etc.
    for col_idx in range(0, box_width, step):
        # Turn off this column and all previous ones
        columns_off = list(range(0, col_idx + 1, step))
        column_configs.append(columns_off)

    print(f"\n[INFO] Testing {len(column_configs)} configurations")

    # Storage for results
    all_camera_images = []
    all_dmd_figs = []

    try:
        for config_idx, columns_off in enumerate(column_configs):
            print(f"\n[INFO] Configuration {config_idx}/{len(column_configs)-1}:")
            print(f"  Columns off: {columns_off if columns_off else 'None (all on)'}")

            # Create DMD pattern
            pattern = create_pattern_with_columns_off(columns_off)

            # Send to DMD
            send_pattern_to_dmd(dmd, pattern)
            print(f"  Pattern sent to DMD")

            # Wait a bit for DMD to settle
            import time
            time.sleep(0.1)

            # Capture camera image
            camera_image = camera.capture_image(num_average=NUM_AVERAGE)
            print(f"  Camera image captured: {camera_image.shape}, max={np.max(camera_image):.1f}")

            # Check saturation
            is_sat, max_val, sat_frac = camera.check_saturation(camera_image)
            if is_sat:
                print(f"  WARNING: Camera saturated! ({sat_frac*100:.2f}% pixels)")

            # Create DMD visualization
            dmd_fig = visualize_dmd_pattern(pattern, columns_off)

            # Store results
            all_camera_images.append(camera_image)
            all_dmd_figs.append(dmd_fig)

            # Save individual files
            config_name = f"config_{config_idx:03d}"

            # Save camera image
            np.save(os.path.join(results_dir, f"{config_name}_camera.npy"), camera_image)

            # Save DMD pattern
            np.save(os.path.join(results_dir, f"{config_name}_dmd_pattern.npy"), pattern)

            # Close DMD figure to save memory
            plt.close(dmd_fig)

        print(f"\n[INFO] All configurations tested. Creating combined plots...")

        # Create combined plots
        create_combined_plots(all_camera_images, column_configs, results_dir)

        print(f"\n[INFO] Experiment complete!")
        print(f"[INFO] Results saved to: {results_dir}/")

    finally:
        # Cleanup
        camera.close()
        print("[INFO] Camera closed")

        # Turn off DMD
        pattern_off = np.zeros((NUM_ROWS, ROW_WIDTH), dtype=np.uint8)
        send_pattern_to_dmd(dmd, pattern_off)
        print("[INFO] DMD cleared")


def create_combined_plots(camera_images, column_configs, save_dir):
    """
    Create combined plots showing DMD config and camera image side by side

    Args:
        camera_images: List of camera images
        column_configs: List of column configurations
        save_dir: Directory to save plots
    """
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

        if len(column_configs[idx]) == 0:
            ax1.set_title('DMD Pattern\nAll columns ON', fontweight='bold')
        else:
            ax1.set_title(f'DMD Pattern\nColumns OFF: {column_configs[idx]}', fontweight='bold')

        plt.colorbar(im1, ax=ax1, label='Pixel State')

        # Camera image
        ax2 = fig.add_subplot(gs[1])
        camera_img = camera_images[idx]
        im2 = ax2.imshow(camera_img, cmap='hot', interpolation='nearest')
        ax2.set_xlabel('X (pixels)', fontweight='bold')
        ax2.set_ylabel('Y (pixels)', fontweight='bold')
        ax2.set_title(f'Camera Image\nMax: {np.max(camera_img):.1f}', fontweight='bold')
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


if __name__ == "__main__":
    print("="*60)
    print("DMD Column Scan Experiment")
    print("="*60)

    # Run with step size of 10 columns
    run_column_scan(step=10)
