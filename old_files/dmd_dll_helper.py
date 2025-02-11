from PIL import Image  # Placeholder if future BMP functionality is added
import ctypes
import os

# Constants
DEVICE_NUMBER = 0  # Typically, 0 for the first connected device
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"  # Path to your DLL
ROW_WIDTH = 1024  # Width of the DMD in pixels
NUM_ROWS = 768  # Height of the DMD in pixels

def load_dll(dll_path):
    """Load the DMD DLL from the provided path and return the handle."""
    try:
        dmd = ctypes.WinDLL(dll_path)
        print(f"Loaded DLL from {dll_path}.")
        return dmd
    except Exception as e:
        raise Exception(f"Failed to load DLL from {dll_path}. Error: {e}")


def get_connected_devices(dmd):
    """Check the number of connected devices."""
    num_devices = dmd.GetNumDev()
    print(f"Number of connected devices: {num_devices}")
    if num_devices < 1:
        raise Exception("No DMD devices found!")
    return num_devices


def get_dmd_type(dmd, device_number):
    """Retrieve the type of the connected DMD device."""
    try:
        dmd_type = dmd.GetDMDTYPE(device_number)
        print(f"DMD TYPE: {dmd_type}")
        return dmd_type
    except Exception as e:
        raise Exception(f"Failed to get DMD type. Error: {e}")


def reset_clear_dmd(dmd, device_number):
    """Clear the DMD display."""
    print("[INFO] Clearing the DMD settings (display does not clear)...")
    clear_result = dmd.ClearFifos(device_number)
    if clear_result == 1:
        print("[SUCCESS] DMD cleared successfully!")
    else:
        raise Exception(f"[ERROR] Failed to clear the DMD. Return code: {clear_result}")


def load_dmd_row(dmd, row_data, row_width, device_number):
    """Load a row of data onto the DMD."""
    dmd_type = get_dmd_type(dmd, device_number)
    load_data_result = dmd.LoadData(
        row_data,
        ctypes.c_uint(row_width),
        dmd_type,  # DMD type !!
        device_number
    )
    if load_data_result != 1:
        raise Exception(f"Failed to load row with return code: {load_data_result}")
    return load_data_result


def block_dimensions(width, height, blocks_x, blocks_y):
    """Calculate block width and height for a given xy division."""
    block_width = width // blocks_x
    block_height = height // blocks_y
    print(f"Block dimensions: {block_width}x{block_height}")
    return block_width, block_height
