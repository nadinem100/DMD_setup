from dmd_dll_class import *
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

from dmd_dll_class import DMD, create_bit_packed_row
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

if __name__ == "__main__":
    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD first
    dmd.reset_clear()

    # Creating a full frame buffer.
    # Each row is bit-packed to ROW_WIDTH/8 bytes; full frame is NUM_ROWS * (ROW_WIDTH/8) bytes.
    full_frame = bytearray()
    for global_row in range(NUM_ROWS):
        white_pixels = 300
        pixel_array = [1] * white_pixels + [0] * (ROW_WIDTH - white_pixels)

        # Bit-pack this row; the result will be 128 bytes.
        row_data_bytes = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
        full_frame.extend(row_data_bytes)

    total_length = len(full_frame)

    # Convert the full_frame bytearray into a ctypes array.
    full_frame_array = (ctypes.c_ubyte * len(full_frame))(*full_frame)

    # Now, load the entire frame in one call.
    dmd.load_row(full_frame_array)

    # Finally, commit the update so the display refreshes.
    dmd.load_control()
    dmd.load_control()
    dmd.load_control()
    print("[INFO] Full frame update committed.")
