from dmd_dll_class import DMD
import ctypes
import time
# import matplotlib.pyplot as plt

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
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD
    dmd.reset_clear()
    # result = dmd.dmd.SetCOMPDATA(0, dmd.device_number)  # InActivate complement mode
    # print("SetCOMPDATA result:", result)  # Should return 1 if successful
    #
    comp_data = ctypes.c_short(dmd.dmd.GetCOMPDATA(dmd.device_number)).value
    print("COMPLEMENT DATA (Expected 1 or 0):", comp_data)
    #
    print('DLL REV:', (dmd.dmd.GetDLLRev()))
    # print("[INFO] Checking current row address...")
    # current_row = dmd.get_row_address()
    # print(f"[INFO] Currently at row address: {current_row}")
    #
    # print("Currently in row address mode: ", dmd.get_row_mode())
    # dmd.set_row_mode(0)
    # print("Currently in row address mode: ", dmd.get_row_mode())
    # dmd.dmd.LoadControl(dmd.device_number)

    # Load data to a specific row
    # # row_index = 200  # Target row
    # for row_index in range(200,300):
    #     dmd.load_specific_row(row_index=row_index, row_data=white_row)
    # for row_index in range(300,400):
    #     dmd.load_specific_row(row_index=row_index, row_data=dark_row)
    # for row_index in range(400,500):
    #     dmd.load_specific_row(row_index=row_index, row_data=white_row)
    # for row_index in range(500,600):
    #     dmd.load_specific_row(row_index=row_index, row_data=dark_row)

    # # Confirm row setting
    # current_row = dmd.get_row_address()
    # print(f"[INFO] Currently at row address: {current_row}")


    # # Create and load black and white rows
    total_rows=[]
    for row in range(NUM_ROWS):
        # if row > 100:
        # print(halfhalf_row)
        black_pixels = 339
        white_pixels = 339
        remaining_pixels = ROW_WIDTH - (black_pixels + white_pixels)  # Fill the gap
        # print(remaining_pixels)

        # Construct the row explicitly
        checkerboard_row = ([0x00] * black_pixels + [0xFF] * white_pixels + [0x00] * remaining_pixels)
        row_data = checkerboard_row[:ROW_WIDTH]
        row_data23= (ctypes.c_ubyte * ROW_WIDTH)(*row_data)
        dmd.load_row(row_data23)
        total_rows.append(row_data)
        # dmd.dmd.ClearFifos(dmd.device_number)  # Clear any pending data
        # dmd.dmd.LoadControl(dmd.device_number)  # Apply control settings
        # dmd.dmd.Clear(17, 1)  # Force a global clear & refresh

    # for _ in range(250):
    #     dmd.load_row(dark_row)

    # for _ in range(NUM_ROWS):
    #     dmd.load_row(halfhalf_row)

