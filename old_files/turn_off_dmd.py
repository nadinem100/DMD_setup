from dmd_dll_class import DMD, create_bit_packed_row
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

# We will split the 768 rows into 2 batches.
BATCH_ROWS = NUM_ROWS // 2  # = 384 rows per batch

if __name__ == "__main__":
    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    dmd.reset_clear()
    dmd.float_mirrors()