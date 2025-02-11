import ctypes

# Load the DLL
dll_path = r"C:\Windows\SysWOW64\D4100_usb.dll"
dmd = ctypes.WinDLL(dll_path)

device_number = 0  # First device
device_num = ctypes.c_short(device_number)

# Step 1: Check if the device is connected
num_devices = dmd.GetNumDev()
if num_devices < 1:
    raise Exception("[ERROR] No DMD devices found! Check connections.")
print(f"[INFO] Number of connected devices: {num_devices}")

# Step 2: Load a blank frame (black image)
row_width = 1024
num_rows = 768
black_row = (ctypes.c_ubyte * row_width)(*([0x00] * row_width))

print("[INFO] Loading black image to clear the DMD...")
for row in range(num_rows):
    load_data_result = dmd.LoadData(black_row, ctypes.c_uint(row_width), ctypes.c_short(0), device_num)
    if load_data_result != 1:
        raise Exception(f"[ERROR] Failed to load row {row} with code: {load_data_result}")

print("[SUCCESS] Black image loaded to DMD.")

# Step 3: Try applying a Micromirror Clocking Pulse
print("[INFO] Sending Micromirror Clocking Pulse...")

# Enable test pattern generator first (some models require this)
enable_tpg = dmd.SetTPGEnable(ctypes.c_short(1), device_num)
if enable_tpg != 1:
    print(f"[WARNING] Test Pattern Generator might not have enabled. Return code: {enable_tpg}")

reset_pulse_result = dmd.LoadControl()

if reset_pulse_result == 1:
    print("[SUCCESS] Micromirror Clocking Pulse applied! Image should now be cleared.")
else:
    print(f"[ERROR] Reset failed. Return code: {reset_pulse_result}")
