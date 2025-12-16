import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from dmd_dll_class import DMD, create_bit_packed_row

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

class MinimalDMDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimal DMD Test")

        # Frame for controls
        control_frame = ttk.LabelFrame(root, text="Pattern Selection", padding=20)
        control_frame.pack(padx=20, pady=20)

        # Top half choice
        ttk.Label(control_frame, text="Top Half:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.top_half = tk.StringVar(value="white")
        ttk.Radiobutton(control_frame, text="White", variable=self.top_half,
                       value="white").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(control_frame, text="Black", variable=self.top_half,
                       value="black").grid(row=0, column=2, padx=5)

        # Bottom half choice
        ttk.Label(control_frame, text="Bottom Half:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.bottom_half = tk.StringVar(value="black")
        ttk.Radiobutton(control_frame, text="White", variable=self.bottom_half,
                       value="white").grid(row=1, column=1, padx=5)
        ttk.Radiobutton(control_frame, text="Black", variable=self.bottom_half,
                       value="black").grid(row=1, column=2, padx=5)

        # Run button
        ttk.Button(root, text="Update DMD Display",
                  command=self.run_test_pattern,
                  padding=20).pack(padx=50, pady=20)

        self.status = ttk.Label(root, text="Select pattern and click button")
        self.status.pack(pady=10)

    def run_test_pattern(self):
        """Run EXACT same code as running_dmd_diffpattern_2loaddata.py"""
        try:
            # Get user choices
            top_color = self.top_half.get()
            bottom_color = self.bottom_half.get()

            self.status.config(text="Updating DMD...", foreground="blue")
            self.root.update()

            print(f"[INFO] Pattern: Top={top_color}, Bottom={bottom_color}")
            print("[INFO] Creating DMD instance...")
            dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER,
                     row_width=ROW_WIDTH, num_rows=NUM_ROWS)

            print("[INFO] Calling reset_clear_old()...")
            dmd.reset_clear_old()

            # Create pattern based on user choice
            print("[INFO] Loading pattern...")
            BATCH_ROWS = NUM_ROWS // 2

            # Top half
            batch1 = bytearray()
            top_value = 0 if top_color == "white" else 1
            for row in range(0, BATCH_ROWS):
                pixel_array = [top_value] * ROW_WIDTH
                row_data = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
                batch1.extend(row_data)

            batch1_array = (ctypes.c_ubyte * len(batch1))(*batch1)
            dmd.load_row(batch1_array)
            dmd.load_control()
            print(f"[INFO] Batch 1 loaded (top half - {top_color})")

            # Bottom half
            batch2 = bytearray()
            bottom_value = 0 if bottom_color == "white" else 1
            for row in range(BATCH_ROWS, NUM_ROWS):
                pixel_array = [bottom_value] * ROW_WIDTH
                row_data = create_bit_packed_row(pixel_array, row_width=ROW_WIDTH)
                batch2.extend(row_data)

            batch2_array = (ctypes.c_ubyte * len(batch2))(*batch2)
            dmd.load_row(batch2_array)
            print(f"[INFO] Batch 2 loaded (bottom half - {bottom_color})")

            # Display it
            print("[INFO] Calling reset_clear()...")
            dmd.reset_clear()

            print("[INFO] Done!")
            self.status.config(text="SUCCESS! Check DMD", foreground="green")
            messagebox.showinfo("Success",
                              f"Pattern loaded!\n\nTop half = {top_color.upper()}\nBottom half = {bottom_color.upper()}")

        except Exception as e:
            error_msg = f"Failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.status.config(text="FAILED", foreground="red")
            messagebox.showerror("Error", error_msg)


def main():
    root = tk.Tk()
    app = MinimalDMDGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
