import win32com.client

# ActiveX things
ddc4100 = win32com.client.Dispatch("DDC4100.DDC4100Ctrl.1")

# Initialize connection to DMD
device_number = 1
firmware_path = r"C:\Program Files (x86)\D4100Explorer\D4100_GUI_FPGA.bin"


result=ddc4100.ConnectDevice(device_number, firmware_path)
if result == 1:
    print("YOU CAN TALK TO THE DDMDDDDDD !!!!")
else:
    print("didnt work sorry bestie")

# except Exception as e:
#     print(f"Error: {e}")