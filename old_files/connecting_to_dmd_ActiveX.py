import win32com.client

# Initialize ActiveX Control
try:
    ddc4100 = win32com.client.Dispatch("DDC4100.DDC4100Ctrl.1")
    print("ActiveX component initialized successfully.")
except Exception as e:
    print(f"Error: Failed to load ActiveX component - {e}")
    exit(1)

# Initialize Connection to DMD
device_number = 1
firmware_path = r"C:\Program Files (x86)\D4100Explorer\D4100_GUI_FPGA.bin"


# Check if the firmware file exists before proceeding
import os

if not os.path.exists(firmware_path):
    raise FileNotFoundError(f"Firmware file not found: {firmware_path}")

# Attempt to connect to the device
result = ddc4100.DownloadAppsFPGACode(firmware_path) #ddc4100.ConnectDevice(device_number, firmware_path)
if result == 1:
    print("Successfully connected to the DMD!")
else:
    print("Failed to connect to the DMD. Check device and firmware.")
# except FileNotFoundError as fe:
#     print(fe)
# except Exception as e:
#     print(f"Error during device connection: {e}")
