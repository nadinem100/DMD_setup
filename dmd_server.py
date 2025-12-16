"""
DMD Server - Run with 32-bit Python
Receives DMD pattern arrays and sends them to the DMD hardware
Communicates via simple file-based protocol
"""

import numpy as np
import ctypes
import time
import os
from dmd_dll_class import DMD, create_bit_packed_row

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

# Communication files
COMMAND_FILE = "dmd_command.txt"
PATTERN_FILE = "dmd_pattern.npy"
STATUS_FILE = "dmd_status.txt"


def send_pattern_to_dmd(dmd, pixel_array):
    """Send pattern to DMD using the working 2-batch method"""
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


def write_status(message):
    """Write status to file"""
    with open(STATUS_FILE, 'w') as f:
        f.write(message)


def run_server():
    """Run the DMD server"""
    print("[DMD SERVER] Starting DMD server (32-bit Python)...")

    # Initialize DMD
    print("[DMD SERVER] Initializing DMD...")
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER,
              row_width=ROW_WIDTH, num_rows=NUM_ROWS)
    dmd.reset_clear_old()
    print("[DMD SERVER] DMD initialized and ready")

    write_status("READY")

    print("[DMD SERVER] Waiting for commands...")
    print("[DMD SERVER] (Write 'QUIT' to dmd_command.txt to exit)")

    try:
        while True:
            # Check for command
            if os.path.exists(COMMAND_FILE):
                with open(COMMAND_FILE, 'r') as f:
                    command = f.read().strip()

                # Delete command file
                os.remove(COMMAND_FILE)

                if command == "QUIT":
                    print("[DMD SERVER] Quit command received")
                    write_status("QUITTING")
                    break

                elif command == "SEND_PATTERN":
                    print("[DMD SERVER] Sending pattern to DMD...")
                    write_status("BUSY")

                    # Load pattern
                    pattern = np.load(PATTERN_FILE)

                    # Send to DMD
                    send_pattern_to_dmd(dmd, pattern)

                    print("[DMD SERVER] Pattern sent successfully")
                    write_status("READY")

                else:
                    print(f"[DMD SERVER] Unknown command: {command}")
                    write_status("READY")

            # Short sleep to avoid busy waiting
            time.sleep(0.01)

    finally:
        # Clear DMD on exit
        print("[DMD SERVER] Clearing DMD...")
        pattern_off = np.zeros((NUM_ROWS, ROW_WIDTH), dtype=np.uint8)
        send_pattern_to_dmd(dmd, pattern_off)
        print("[DMD SERVER] DMD server stopped")
        write_status("STOPPED")


if __name__ == "__main__":
    run_server()
