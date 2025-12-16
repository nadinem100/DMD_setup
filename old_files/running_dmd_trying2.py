from dmd_dll_class import *
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768


if __name__ == "__main__":
    # Constants for the DMD
    DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
    DEVICE_NUMBER = 0
    ROW_WIDTH = 1024
    NUM_ROWS = 768

    # For a DLP7000-type DMD (1024x768), there are 16 blocks of 48 rows.
    BLOCK_HEIGHT = 48

    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD
    dmd.reset_clear()

    # Create and load rows with different patterns
    for global_row in range(NUM_ROWS):
        # Calculate block number and row within block
        block = 6 #global_row // BLOCK_HEIGHT       # integer division
        row_in_block = global_row % BLOCK_HEIGHT

        # Set the proper block and row addresses
        dmd.set_block_address(block)
        dmd.set_row_address(row_in_block)

        # Choose a pattern based on the global row index
        if global_row < NUM_ROWS // 2:
            # For the first half: 400 white pixels followed by black pixels
            white_pixels = 500
            black_pixels = ROW_WIDTH - white_pixels
            pixel_array = [0] * white_pixels + [1] * black_pixels
        else:
            # For the second half: 624 white pixels followed by black pixels
            white_pixels = 500
            black_pixels = ROW_WIDTH - white_pixels
            pixel_array = [1] * white_pixels + [0] * black_pixels

        # Bit-pack the row data (resulting length will be ROW_WIDTH//8)
        row_data_bytes = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
        uchar_array = (ctypes.c_ubyte * len(row_data_bytes))(*row_data_bytes)

        # Load the row data
        dmd.load_row(uchar_array)
        # print(f"[INFO] Loaded data for global row {global_row} (block {block}, row {row_in_block}).")
        # commit the loaded data:
        # if row_in_block % BLOCK_HEIGHT == 0:
        #     commit = dmd.dmd.LoadControl(ctypes.c_short(dmd.device_number))
        #     commit = dmd.dmd.LoadControl(ctypes.c_short(dmd.device_number))
        #     commit = dmd.dmd.LoadControl(ctypes.c_short(dmd.device_number))
        #     if commit != 1:
        #         print(f"[WARNING] LoadControl commit returned {commit}")


    dmd.load_control()
    dmd.load_control()
    dmd.load_control()