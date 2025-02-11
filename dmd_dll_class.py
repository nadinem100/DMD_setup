import ctypes

class DMD:
    def __init__(self, dll_path=r"C:\Windows\SysWOW64\D4100_usb.dll", device_number=0, row_width=1024, num_rows=768):
        """
        Initialize the DMD instance.
        :param dll_path: Path to the DMD DLL.
        :param device_number: Device number (default: 0 for the first connected device).
        :param row_width: Width of the DMD in pixels (default: 1024).
        :param num_rows: Height of the DMD in pixels (default: 768).
        """
        self.dll_path = dll_path
        self.device_number = device_number
        self.row_width = row_width
        self.num_rows = num_rows
        self.block_height = 48

        # Load the DLL
        self.dmd = self._load_dll()

        # Check devices
        self.num_devices = self.get_connected_devices()

        # Verify DMD type (for example, DLP7000 type may be returned as 1)
        self.dmd_type = self.get_dmd_type()

    def _load_dll(self):
        """Load the DMD DLL."""
        try:
            dmd = ctypes.WinDLL(self.dll_path)
            print(f"[INFO] Loaded DLL from {self.dll_path}.")
            return dmd
        except Exception as e:
            raise Exception(f"[ERROR] Failed to load DLL from {self.dll_path}. Error: {e}")

    def get_connected_devices(self):
        """Return the number of connected devices."""
        num_devices = self.dmd.GetNumDev()
        print(f"[INFO] Number of connected devices: {num_devices}")
        if num_devices < 1:
            raise Exception("[ERROR] No DMD devices found!")
        return num_devices

    def get_dmd_type(self):
        """Retrieve and return the type of the connected DMD device."""
        try:
            dmd_type = self.dmd.GetDMDTYPE(ctypes.c_short(self.device_number))
            print(f"[INFO] DMD TYPE: {dmd_type}")
            return dmd_type
        except Exception as e:
            raise Exception(f"[ERROR] Failed to get DMD type. Error: {e}")

    def reset_clear(self):
        """Clear the DMD display."""
        # Example calls – adjust according to your DLL API
        self.dmd.SetRST2BLKZ(ctypes.c_short(0), ctypes.c_short(self.device_number))
        print('After setting RST2BLKZ to 0, value is:',
              self.dmd.GetRST2BLKZ(ctypes.c_short(self.device_number)))
        print('Current row mode:', self.dmd.GetRowMd(ctypes.c_short(self.device_number)))
        success = self.dmd.SetRowMd(ctypes.c_short(1), ctypes.c_short(self.device_number))
        print('RowMd set result (1 if successful):', success)

        # Commit control values
        for _ in range(3):
            control_result = self.dmd.LoadControl(ctypes.c_short(self.device_number))
        if control_result == 1:
            print("[SUCCESS] LoadControl committed.")
        else:
            raise Exception(f"[ERROR] Failed to LoadControl. Return code: {control_result}")

        print("[INFO] Clearing the DMD display...")
        clear_result = self.dmd.ClearFifos(ctypes.c_short(self.device_number))
        if clear_result == 1:
            print("[SUCCESS] DMD cleared successfully!")
        else:
            raise Exception(f"[ERROR] Failed to ClearFifos. Return code: {clear_result}")

    def load_row(self, row_data):
        """
        Load a row of data onto the DMD.
        :param row_data: The row data as a ctypes array of c_ubyte.
        """
        # Use the actual length (number of bytes in the packed row)
        data_length = len(row_data)
        load_data_result = self.dmd.LoadData(
            row_data,                                # RowData: ctypes array of unsigned char
            ctypes.c_uint(data_length),              # Length: number of bytes in row_data
            ctypes.c_short(self.dmd_type),           # DMDType: type of the connected DMD
            ctypes.c_short(self.device_number)       # DeviceNumber: typically 0
        )
        if load_data_result != 1:
            raise Exception(f"[ERROR] Failed to load row. DMDType: {self.dmd_type}, Return code: {load_data_result}")
        # commit the loaded data:
        commit = self.dmd.LoadControl(ctypes.c_short(self.device_number))
        if commit != 1:
            print(f"[WARNING] LoadControl commit returned {commit}")

    def set_row_address(self, row_index):
        """Set the target row address (within the current block) in the ROWAD register."""
        result = self.dmd.SetRowAddr(ctypes.c_short(row_index), ctypes.c_short(self.device_number))
        if result != 1:
            raise Exception(f"[ERROR] Failed to set row address to {row_index}")
        # print(f"[INFO] Row address set to {row_index}.")

    def set_block_address(self, block):
        """Set the target block address (BLKAD register)."""
        result = self.dmd.SetBlkAd(ctypes.c_short(block), ctypes.c_short(self.device_number))
        if result != 1:
            raise Exception(f"[ERROR] Failed to set block address to {block}")
        # print(f"[INFO] Block address set to {block}.")

    def commit_frame(self):
        """Commit the full frame (or block) update by calling LoadControl once."""
        commit = self.dmd.LoadControl(ctypes.c_short(self.device_number))
        if commit != 1:
            raise Exception(f"[ERROR] Final LoadControl commit returned {commit}")
        print("[INFO] Frame updated successfully.")


# Utility function to create a bit-packed row from a pixel array
def create_bit_packed_row(pixel_array, row_width=1024):
    """
    Convert a list of 0/1 values (length = row_width) into a byte array
    where 8 pixels are packed into one byte.
    """
    packed_bytes = bytearray()
    for i in range(0, row_width, 8):  # process 8 pixels at a time
        byte = 0  # start with 00000000
        for bit in range(8):
            if i + bit < len(pixel_array):
                # Shift the bit into the correct position (bit 7 is the leftmost pixel)
                byte |= (pixel_array[i + bit] & 0x01) << (7 - bit)
        packed_bytes.append(byte)
    return packed_bytes

