from dmd_dll_class import DMD
import ctypes
import time

# import plotly.graph_objects as go
# import matplotlib.pyplot as plt

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768


def create_bit_packed_row(pixel_array, row_width=1024):

    # Convert this into a bit-packed byte array
    packed_bytes = bytearray()

    for i in range(0, row_width, 8): #process every 8 pixels as 1 byte
        byte = 0 #start w empty byte = 00000000
        for bit in range(8):
            if i + bit < row_width:
                # pixel_array[i + bit] is either 0 or 1 (white or dark)
                # << n is like setting that index of the array to that value
                # |= is like bitwise OR, and then re-assigns byte to be that (like +=)
                byte |= (pixel_array[i + bit] << (7 - bit))  # set bits from left to right
        packed_bytes.append(byte)

    #debugging
    for byte in packed_bytes:
        print(f"{byte}")

    # Convert to ctypes uchar* (unsigned char pointer)
    # uchar_array = (ctypes.c_ubyte * len(packed_bytes))(*packed_bytes)

    return packed_bytes

if __name__ == "__main__":
    dark_row = [0x00] * ROW_WIDTH
    white_row = [0xFF] * ROW_WIDTH
    halfhalf_row = [0x00] * (ROW_WIDTH//2) + [0xFF] * (ROW_WIDTH//2)

    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD
    dmd.reset_clear()

    comp_data = ctypes.c_short(dmd.dmd.GetCOMPDATA(dmd.device_number)).value
    print("COMPLEMENT DATA (Expected 1 or 0):", comp_data)
    #
    print('DLL REV:', (dmd.dmd.GetDLLRev()))


# Create and load black and white rows
    ALL_row_data=bytearray()
    for row in range(NUM_ROWS):

        black_pixels = 400
        white_pixels = 400
        remaining_pixels = ROW_WIDTH - (black_pixels + white_pixels)  # Fill the gap

        # if row < NUM_ROWS/2:
            # Construct the row explicitly
            # checkerboard_row = ([0x00] * black_pixels + [0xFF] * white_pixels + [0x00] * remaining_pixels)
            # row_data = checkerboard_row[:ROW_WIDTH]
            # assert black_pixels + white_pixels <= row_width, "Total pixels exceed row width!"

            # desired array of 0s (white) and 1s (black), this is messed up rn
        pixel_array = [1] * black_pixels + [0] * white_pixels + [1] * remaining_pixels

        # else:
        #     pixel_array = [0] * black_pixels + [1] * white_pixels + [0] * remaining_pixels

        row_data23 = create_bit_packed_row(pixel_array)
        # ALL_row_data.extend(row_data23)

        uchar_array = (ctypes.c_ubyte * ROW_WIDTH)(*row_data23)
        # uchar_array = (ctypes.c_ubyte * len(ALL_row_data))(*ALL_row_data)
        dmd.load_row(uchar_array)
        # total_rows.append(row_data)




