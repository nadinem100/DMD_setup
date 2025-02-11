from dmd_dll_helper import *
import ctypes

# Loading the DLL
dll_path = r"C:\Windows\SysWOW64\D4100_usb.dll"
dmd = ctypes.WinDLL(dll_path)

# Constants
device_number = 0  # Typically, 0 for the first connected device
firmware_path = b"C:\\Program Files (x86)\\D4100Explorer\\D4100_GUI_FPGA.bin"
bmp_file_path = b"C:\\Program Files (x86)\\D4100Explorer\\Scripts\\WXGA\\checker1.bmp"  # Path to the BMP file
row_width = 1024  # Width of the DMD in pixels
num_rows = 768  # Height of the DMD in pixels


# Check for connected devices
num_devices = dmd.GetNumDev()
print(f"Number of connected devices: {num_devices}")
if num_devices < 1:
    raise Exception("No DMD devices found!")

print('DMD TYPE!', dmd.GetDMDTYPE(device_number))

print("[INFO] Clearing the DMD display...")
clear_result = dmd.ClearFifos(device_number)

if clear_result == 1:
    print("[SUCCESS] DMD cleared successfully!")
else:
    print(f"[ERROR] Failed to clear DMD. Return code: {clear_result}")

black_row = (ctypes.c_ubyte * row_width)(*([0x00] * row_width))

for row in range(num_rows):
    load_data_result = 1
    dmd.LoadData(black_row, ctypes.c_uint(row_width), ctypes.c_short(1  ), device_number)
    if load_data_result != 1:
        raise Exception(f"[ERROR] Failed to load row {row} with code: {load_data_result}")

# half_width = row_width // 2
# half_black_half_white_row = (ctypes.c_ubyte * row_width)(*(
#         [0x00] * half_width + [0xFF] * (row_width - half_width)
# ))
#
# # Send the row data to the DMD
# for row in range(num_rows):
#     load_data_result = dmd.LoadData(
#         half_black_half_white_row,
#         ctypes.c_uint(row_width),
#         ctypes.c_short(1),  # Single-row loading
#         device_number
#     )
# clear_succes = dmd.Clear(17, 1)
# print('clear was sucessful (if 1, then success)', clear_succes)

# dmd.SetEXTRESETENBL(0)
# set_result = dmd.SetEXTRESETENBL(ctypes.c_short(1), device_number)
# if set_result == 1:
#     print("[SUCCESS] External reset mode enabled.")
# else:
#     print(f"[ERROR] Failed to enable external reset. Return code: {set_result}")
#
#
# reset_enable_status = ctypes.c_short(dmd.GetEXTRESETENBL()).value
#
# print("getting the external reset enable value:", reset_enable_status)
# dmd.SetEXTRESETENBL(ctypes.c_short(0))

# block_num = ctypes.c_short(17)  # 17 = Global Reset
# reset_result = dmd.GetEXTRESETENBL(block_num)
# if reset_result == 1:
#     print("[SUCCESS] Global reset issued.")
# else:
#     print(f"[ERROR] Failed to issue global reset. Return code: {reset_result}")
#
#
# # Step 2: Wait for the reset to complete
# reset_status = dmd.GetRESETCOMPLETE(0, device_number)
#
# if reset_status == 1:
#     print("[SUCCESS] Reset detected successfully!")
# elif reset_status == 0:
#     print("[INFO] No reset detected within the wait time.")
# else:
#     print(f"[ERROR] Unexpected return value from GetRESETCOMPLETE: {reset_status}")
#
# reset_clear_dmd(dmd, device_number)