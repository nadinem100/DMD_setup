from dmd_dll_class import DMD
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

def create_bit_packed_row(pixel_array, row_width=1024):
    """
    Convert a list of 0/1 values (length = row_width) into a byte array
    where 8 pixels are packed into one byte.
    """
    packed_bytes = bytearray()
    for i in range(0, row_width, 8):  # process 8 pixels at a time
        byte = 0  # start with 00000000
        for bit in range(8):
            if i + bit < len(pixel_array):
                # Shift the bit into the correct position (bit 7 is the leftmost pixel)
                byte |= (pixel_array[i + bit] & 0x01) << (7 - bit)
        packed_bytes.append(byte)
    return packed_bytes

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
        block = global_row // BLOCK_HEIGHT       # integer division
        row_in_block = global_row % BLOCK_HEIGHT

        # Set the proper block and row addresses
        dmd.set_block_address(block)
        dmd.set_row_address(row_in_block)

        # Choose a pattern based on the global row index
        if global_row < NUM_ROWS // 2:
            # For the first half: 400 white pixels followed by black pixels
            white_pixels = 500
            black_pixels = ROW_WIDTH - white_pixels
            pixel_array = [1] * white_pixels + [0] * black_pixels
        else:
            # For the second half: 624 white pixels followed by black pixels
            white_pixels = 500
            black_pixels = ROW_WIDTH - white_pixels
            pixel_array = [0] * white_pixels + [1] * black_pixels

        # Bit-pack the row data (resulting length will be ROW_WIDTH//8)
        row_data_bytes = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
        uchar_array = (ctypes.c_ubyte * len(row_data_bytes))(*row_data_bytes)

        # Load the row data
        dmd.load_row(uchar_array)
        # print(f"[INFO] Loaded data for global row {global_row} (block {block}, row {row_in_block}).")

    dmd.commit_frame()