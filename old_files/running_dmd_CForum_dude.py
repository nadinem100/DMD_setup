from dmd_dll_class import DMD, create_bit_packed_row
import ctypes

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

# We will split the 768 rows into 2 batches.
BATCH_ROWS = NUM_ROWS // 2  # = 384 rows per batch

if __name__ == "__main__":
    # Create the DMD instance
    dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER, row_width=ROW_WIDTH, num_rows=NUM_ROWS)

    # Clear the DMD display first
    # dmd.reset_clear()
    # dmd.dmd.SetBlkAd(ctypes.c_short(0), dmd.device_number)

    # Build batch 1 (global rows 0 to 383)
    batch1 = bytearray()
    for global_row in range(0, BATCH_ROWS):
        # let the first 300 pixels be 0 and the rest 1.
        white_pixels = 500
        pixel_array = [0] * white_pixels + [1] * (ROW_WIDTH - white_pixels)
        row_data_bytes = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
        batch1.extend(row_data_bytes)
    total_length_batch1 = len(batch1)
    print(f"[INFO] Batch1 length: {total_length_batch1} bytes (should be {BATCH_ROWS * (ROW_WIDTH // 8)}).")

    # Convert batch1 to a ctypes array
    # batch1_array = (ctypes.c_ubyte * total_length_batch1).from_buffer_copy(batch1)
    batch1_array = (ctypes.c_ubyte * len(batch1))(*batch1)

    # Load the first half of the frame (batch 1)
    dmd.load_row(batch1_array)
    dmd.load_control()

    print("[INFO] Batch 1 loaded (rows 0 to 383).")

    # Build batch 2 (global rows 384 to 767)
    batch2 = bytearray()
    for global_row in range(BATCH_ROWS, NUM_ROWS):
        white_pixels = 500
        pixel_array = [1] * white_pixels + [0] * (ROW_WIDTH - white_pixels)
        row_data_bytes = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
        batch2.extend(row_data_bytes)
    total_length_batch2 = len(batch2)
    print(f"[INFO] Batch2 length: {total_length_batch2} bytes (should be {BATCH_ROWS * (ROW_WIDTH // 8)}).")

    # Convert batch2 to a ctypes array
    # batch2_array = (ctypes.c_ubyte * total_length_batch2).from_buffer_copy(batch2)
    batch2_array = (ctypes.c_ubyte * len(batch2))(*batch2)

    # Load the second half of the frame (batch 2)
    dmd.load_row(batch2_array)
    print("[INFO] Batch 2 loaded (rows 384 to 767).")

    # dmd.dmd.SetBlkMd(ctypes.c_short(3), dmd.device_number)
    # dmd.dmd.SetBlkAd(ctypes.c_short(8), dmd.device_number)
    # # Finally, commit the entire frame update with one call.
    dmd.load_control()
    dmd.load_control()
    dmd.load_control()
    # print("[INFO] Full frame update committed.")
