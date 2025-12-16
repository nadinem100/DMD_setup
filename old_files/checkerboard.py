from dmd_dll_class import DMD
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768
BLOCKS_X = 9  # Number of blocks horizontally
BLOCKS_Y = 1  # Number of blocks vertically


def create_checkerboard_row(row, block_width, block_height, row_width):
    """
    Creates a checkerboard-style row based on row position.
    :param row: The current row index.
    :param block_width: Width of each block.
    :param block_height: Height of each block.
    :param row_width: Total row width.
    :return: Row data as ctypes array.
    """
    # Determine which vertical block the row belongs to
    row_block = row // block_height

    # Alternate starting color based on the row block
    start_with_black = (row_block % 2 == 0)

    row_data = []
    for col_block in range(BLOCKS_X):
        if (col_block % 2 == 0 and start_with_black) or (col_block % 2 != 0 and not start_with_black):
            row_data.extend([0x00] * block_width)  # Black block
        else:
            row_data.extend([0xFF] * block_width)  # White block

    # Ensure the row matches the width of the DMD
    row_data = row_data[:row_width]
    print(row_data)
    return (ctypes.c_ubyte * row_width)(*row_data)


if __name__ == "__main__":
    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD
    dmd.reset_clear()

    # Calculate block dimensions
    block_width, block_height = dmd.calculate_block_dimensions(ROW_WIDTH, NUM_ROWS, BLOCKS_X, BLOCKS_Y)

    # Create and load checkerboard rows
    for row in range(NUM_ROWS):
        checkerboard_row = create_checkerboard_row(row, block_width, block_height, ROW_WIDTH)
        # checkerboard_row = ([0] * 128 + [255] * 128) * 4

        # print(checkerboard_row)
        dmd.load_row(checkerboard_row)
