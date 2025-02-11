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

        # Load the DLL
        self.dmd = self._load_dll()

        # Check devices
        self.num_devices = self.get_connected_devices()

        # Verify DMD type
        self.dmd_type = self.get_dmd_type()

    def _load_dll(self):
        """Private method to load the DMD DLL."""
        try:
            dmd = ctypes.WinDLL(self.dll_path)
            print(f"[INFO] Loaded DLL from {self.dll_path}.")
            return dmd
        except Exception as e:
            raise Exception(f"[ERROR] Failed to load DLL from {self.dll_path}. Error: {e}")

    def get_connected_devices(self):
        """Check and return the number of connected devices."""
        num_devices = self.dmd.GetNumDev()
        print(f"[INFO] Number of connected devices: {num_devices}")
        if num_devices < 1:
            raise Exception("[ERROR] No DMD devices found!")
        return num_devices

    def get_dmd_type(self):
        """Retrieve and return the type of the connected DMD device."""
        try:
            dmd_type = self.dmd.GetDMDTYPE(self.device_number)
            print(f"[INFO] DMD TYPE: {dmd_type}")
            return dmd_type
        except Exception as e:
            raise Exception(f"[ERROR] Failed to get DMD type. Error: {e}")

    def reset_clear(self):
        """Clear the DMD display."""
        self.dmd.SetRST2BLKZ(ctypes.c_short(0), ctypes.c_short(self.device_number))
        print('After setting RST2BLKZ to 0, value is:', self.dmd.GetRST2BLKZ(ctypes.c_short(self.device_number)))
        print('Current row mode:', self.dmd.GetRowMd(ctypes.c_short(self.device_number)))
        success = self.dmd.SetRowMd(ctypes.c_short(1), ctypes.c_short(self.device_number))
        print('RowMd set result (1 if successful):', success)

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

        :param row_data: The row data as a Python list or ctypes array.
        """
        # Automatically convert Python list to ctypes array if provided
        if isinstance(row_data, list):
            # if len(row_data) != self.row_width:
            #     raise ValueError(f"[ERROR] The length of the row data must match the DMD row width: {self.row_width}")
            row_data = (ctypes.c_ubyte * self.row_width)(*row_data)

        elif not isinstance(row_data, (ctypes.Array, ctypes._SimpleCData)):
            raise TypeError("[ERROR] row_data must be either a Python list or a ctypes array")

        # Call the DLL function to load the row
        # print(list(row_data))
        load_data_result = self.dmd.LoadData(
            row_data,  # RowData: ctypes array of unsigned char
            ctypes.c_uint(self.row_width),  # Length: size of the row in pixels
            # ctypes.c_uint(len(row_data)),
            ctypes.c_short(self.dmd_type),  # DMDType: type of the connected DMD
            ctypes.c_short(self.device_number)  # DeviceNumber: device identifier, typically 0
        )

        if load_data_result != 1:
            raise Exception(f"[ERROR] Failed to load row. DMDType: {self.dmd_type}, Return code: {load_data_result}")

        # print("[INFO] Row loaded successfully.")

    def set_row_address(self, row_index):
        """Set the target row address in the ROWAD register."""
        result = self.dmd.SetRowAddr(ctypes.c_short(row_index), ctypes.c_short(self.device_number))
        if result != 1:
            raise Exception(f"[ERROR] Failed to set row address to {row_index}")
        # print(f"[INFO] Row address set to {row_index}.")

    def set_row_mode(self, mode_value):
        """Set the row mode in the ROWMD register."""
        result = self.dmd.SetRowMd(ctypes.c_short(mode_value), ctypes.c_short(self.device_number))
        if result != 1:
            raise Exception(f"[ERROR] Failed to set row mode to {mode_value}")
        print(f"[INFO] Row mode set to {mode_value}.")

    def get_row_address(self):
        """Get the current row address from the ROWAD register."""
        row_addr = self.dmd.GetRowAddr(ctypes.c_short(self.device_number))
        print(f"[INFO] Current row address: {row_addr}")
        return row_addr

    def get_row_mode(self):
        """Get the current row address from the ROWMD register."""
        row_md = self.dmd.GetRowMd(ctypes.c_short(self.device_number))
        print(f"[INFO] Current row address: {row_md}")
        return row_md

    def load_specific_row(self, row_index, row_data):
        """Set specific data for a single row."""
        # Set the row address
        self.set_row_address(row_index)

        # Prepare the row data
        if isinstance(row_data, list):
            row_data = (ctypes.c_ubyte * len(row_data))(*row_data)

        # Load the row data
        result = self.dmd.LoadData(
            row_data,
            ctypes.c_uint(len(row_data)),  # Row width
            ctypes.c_short(self.dmd_type),  # DMDType
            ctypes.c_short(self.device_number)
        )

        if result != 1:
            raise Exception(f"[ERROR] Failed to load data for row {row_index}.")
        print(f"[INFO] Data successfully loaded for row {row_index}.")


    @staticmethod
    def calculate_block_dimensions(width, height, blocks_x, blocks_y):
        """
        Calculate block dimensions for dividing the DMD into a grid.

        :param width: Total width.
        :param height: Total height.
        :param blocks_x: Number of blocks horizontally.
        :param blocks_y: Number of blocks vertically.
        :return: Block width and height.
        """
        block_width = width // blocks_x
        block_height = height // blocks_y
        print(f"[INFO] Block dimensions: {block_width}x{block_height}")
        return block_width, block_height
