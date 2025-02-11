import ctypes

# Loading DLL path
dll_path = r"C:\Windows\SysWOW64\D4100_usb.dll"
dmd = ctypes.WinDLL(dll_path)

# Initializing device
device_number = 0
firmware_path = b"C:\\Program Files (x86)\\D4100Explorer\\D4100_GUI_FPGA.bin"

try:
    num_devices = dmd.GetNumDev()
    print(f"Number of devices: {num_devices}")

    dmd_type = dmd.GetDescriptor(1)
    print(f"DMD type: {dmd_type}")


    result=dmd.ConnectDevice(device_number, firmware_path)
    if result == 1:
        print("YOU CAN TALK TO THE DDMDDDDDD !!!!")
    else:
        print("didnt work sorry bestie")

except Exception as e:
    print(f"Error: {e}")