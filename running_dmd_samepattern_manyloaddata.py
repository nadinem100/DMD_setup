from dmd_dll_class import DMD
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

def create_bit_packed_row(pixel_array, row_width=1024):
    # Convert this into a bit-packed byte array
    packed_bytes = bytearray()
    for i in range(0, row_width, 8):  # process every 8 pixels as 1 byte
        byte = 0  # start with an empty byte = 00000000
        for bit in range(8):
            if i + bit < row_width:
                byte |= (pixel_array[i + bit] << (7 - bit))  # set bits from left to right
        packed_bytes.append(byte)
    return packed_bytes

if __name__ == "__main__":
    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD
    dmd.reset_clear()

    # Create and load rows with different patterns
    for row in range(NUM_ROWS):
        white_pixels = 300
        black_pixels = ROW_WIDTH - white_pixels
        pixel_array = [1] * white_pixels + [0] * black_pixels

        row_data = create_bit_packed_row(pixel_array)
        uchar_array = (ctypes.c_ubyte * len(row_data))(*row_data)
        dmd.load_row(uchar_array)