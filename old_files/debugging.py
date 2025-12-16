import ctypes
from dmd_dll_class import *
import time

DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

# Test script
try:
    print("[INFO] Loading DMD DLL...")
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)
    print("[INFO] Initialized DMD successfully.")

    # Reset the DMD
    print("[INFO] Clearing DMD...")
    dmd.reset_clear()

    # Define row patterns
    white_row = [0xFF] * ROW_WIDTH
    black_row = [0x00] * ROW_WIDTH
    halfhalf_row = [0x00] * (ROW_WIDTH // 2) + [0xFF] * (ROW_WIDTH // 2)

    # Test loading a few rows
    print("[INFO] Starting row data test...")
    for i in range(10):  # Change only the first 10 rows for testing
        dmd.load_row(halfhalf_row)
        time.sleep(0.01)  # Small delay for hardware stability

    print("[INFO] Data test complete.")

except Exception as e:
    print(f"[ERROR] Test failed: {e}")
