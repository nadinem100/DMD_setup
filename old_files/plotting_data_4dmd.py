from dmd_dll_class import DMD
import ctypes
import time

import matplotlib.pyplot as plt
import numpy as np

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

if __name__ == "__main__":
    dark_row = [0x00] * ROW_WIDTH
    white_row = [0xFF] * ROW_WIDTH
    halfhalf_row = [0x00] * (ROW_WIDTH//2) + [0xFF] * (ROW_WIDTH//2)

    # Create the DMD instance
    # dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD
    # dmd.reset_clear()

    # comp_data = ctypes.c_short(dmd.dmd.GetCOMPDATA(dmd.device_number)).value
    # print("COMPLEMENT DATA (Expected 1 or 0):", comp_data)
    #
    # print('DLL REV:', (dmd.dmd.GetDLLRev()))


# Create and load black and white rows
    total_rows=[]
    for row in range(NUM_ROWS):

        black_pixels = 339
        white_pixels = 339
        remaining_pixels = ROW_WIDTH - (black_pixels + white_pixels)  # Fill the gap


        # Construct the row explicitly
        checkerboard_row = ([0x00] * black_pixels + [0xFF] * white_pixels + [0x00] * remaining_pixels)
        row_data = checkerboard_row[:ROW_WIDTH]
        row_data23= (ctypes.c_ubyte * ROW_WIDTH)(*row_data)
        # dmd.load_row(row_data23)
        total_rows.append(row_data)

    # # Plot and display the rows after loop
    plt.imshow(np.array(total_rows), cmap='gray', aspect='auto')
    plt.show()







