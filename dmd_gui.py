import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ctypes
import numpy as np
from PIL import Image
from dmd_dll_class import DMD, create_bit_packed_row

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

class EnhancedDMDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced DMD Controller")

        # DMD state
        self.dmd = None
        self.dmd_initialized = False

        # Pixel array (1 = black/off, 0 = white/on)
        self.pixel_array = np.zeros((NUM_ROWS, ROW_WIDTH), dtype=np.uint8)

        # Display scaling - show every 4th pixel
        self.scale = 4
        self.pixel_size = 6  # Size of each displayed pixel (adjustable with zoom)

        # Drawing state
        self.is_dragging = False

        # Undo history (store up to 20 states)
        self.history = []
        self.max_history = 20

        self.setup_gui()

    def setup_gui(self):
        # Top control frame
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # DMD control buttons
        ttk.Button(top_frame, text="1. Initialize DMD",
                  command=self.init_dmd).pack(side=tk.LEFT, padx=5)

        self.update_btn = ttk.Button(top_frame, text="2. Update Display",
                                     command=self.update_display, state=tk.DISABLED)
        self.update_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(top_frame, text="All Off",
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)

        ttk.Button(top_frame, text="All On",
                  command=self.fill_all).pack(side=tk.LEFT, padx=5)

        ttk.Button(top_frame, text="Save BMP",
                  command=self.save_bmp).pack(side=tk.LEFT, padx=5)

        ttk.Button(top_frame, text="Undo",
                  command=self.undo).pack(side=tk.LEFT, padx=5)

        # Status
        self.status = ttk.Label(top_frame, text="Not initialized", foreground="red")
        self.status.pack(side=tk.LEFT, padx=20)

        # Drawing mode frame
        mode_frame = ttk.LabelFrame(self.root, text="Drawing Tools", padding="10")
        mode_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.draw_mode = tk.StringVar(value="toggle")
        ttk.Radiobutton(mode_frame, text="Toggle (Click)", variable=self.draw_mode,
                       value="toggle").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Paint On (Drag)", variable=self.draw_mode,
                       value="paint").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Paint Off (Drag)", variable=self.draw_mode,
                       value="erase").pack(side=tk.LEFT, padx=5)

        ttk.Label(mode_frame, text="Brush Size:").pack(side=tk.LEFT, padx=(20, 5))
        self.brush_size = tk.IntVar(value=1)
        ttk.Spinbox(mode_frame, from_=1, to=10, textvariable=self.brush_size,
                   width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(mode_frame, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(mode_frame, text="+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(mode_frame, text="-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=2)

        # Quick patterns frame
        pattern_frame = ttk.LabelFrame(self.root, text="Quick Patterns", padding="10")
        pattern_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Button(pattern_frame, text="Top Half Off",
                  command=lambda: self.apply_pattern("top_white")).pack(side=tk.LEFT, padx=5)
        ttk.Button(pattern_frame, text="Top Half On",
                  command=lambda: self.apply_pattern("top_black")).pack(side=tk.LEFT, padx=5)
        ttk.Button(pattern_frame, text="Bottom Half Off",
                  command=lambda: self.apply_pattern("bottom_white")).pack(side=tk.LEFT, padx=5)
        ttk.Button(pattern_frame, text="Bottom Half On",
                  command=lambda: self.apply_pattern("bottom_black")).pack(side=tk.LEFT, padx=5)

        # Canvas frame with scrollbars
        canvas_container = ttk.Frame(self.root)
        canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Info label frame
        info_frame = ttk.Frame(canvas_container)
        info_frame.pack(side=tk.TOP, fill=tk.X)

        self.info_label = ttk.Label(info_frame, text="", font=('Arial', 8))
        self.info_label.pack(side=tk.LEFT)

        self.hover_label = ttk.Label(info_frame, text="", font=('Arial', 8), foreground="blue")
        self.hover_label.pack(side=tk.RIGHT, padx=10)

        self.update_info_label()

        # Canvas with scrollbars
        display_rows = NUM_ROWS // self.scale
        display_cols = ROW_WIDTH // self.scale
        canvas_width = min(800, display_cols * self.pixel_size)
        canvas_height = min(600, display_rows * self.pixel_size)

        h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(canvas_container,
                               width=canvas_width,
                               height=canvas_height,
                               bg='white',
                               xscrollcommand=h_scroll.set,
                               yscrollcommand=v_scroll.set)

        h_scroll.config(command=self.canvas.xview)
        v_scroll.config(command=self.canvas.yview)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_hover)

        # Draw initial grid
        self.draw_grid()
        self.update_scroll_region()

    def save_state(self):
        """Save current state to history for undo"""
        # Make a copy of the current pixel array
        state = self.pixel_array.copy()
        self.history.append(state)

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def undo(self):
        """Undo the last change"""
        if len(self.history) > 0:
            # Restore the last saved state
            self.pixel_array = self.history.pop()
            self.draw_grid()
            print(f"[INFO] Undo successful ({len(self.history)} states remaining)")
        else:
            messagebox.showinfo("Undo", "Nothing to undo!")
            print("[INFO] No undo history available")

    def update_info_label(self):
        """Update the info label with current scale and pixel size"""
        display_rows = NUM_ROWS // self.scale
        display_cols = ROW_WIDTH // self.scale
        info_text = f"Grid Display: {display_cols}x{display_rows} (1:{self.scale} scale) | Actual DMD: {ROW_WIDTH}x{NUM_ROWS} | Pixel Size: {self.pixel_size}px"
        self.info_label.config(text=info_text)

    def update_scroll_region(self):
        """Update the canvas scroll region based on current zoom"""
        display_rows = NUM_ROWS // self.scale
        display_cols = ROW_WIDTH // self.scale
        total_width = display_cols * self.pixel_size
        total_height = display_rows * self.pixel_size
        self.canvas.configure(scrollregion=(0, 0, total_width, total_height))

    def draw_grid(self):
        """Draw the pixel grid"""
        self.canvas.delete("all")
        self.rects = {}

        display_rows = NUM_ROWS // self.scale
        display_cols = ROW_WIDTH // self.scale

        for r in range(display_rows):
            for c in range(display_cols):
                x1 = c * self.pixel_size
                y1 = r * self.pixel_size
                x2 = x1 + self.pixel_size
                y2 = y1 + self.pixel_size

                # Get actual pixel value
                actual_r = r * self.scale
                actual_c = c * self.scale
                val = self.pixel_array[actual_r, actual_c]

                color = 'black' if val == 1 else 'white'
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill=color, outline='gray')
                self.rects[(r, c)] = rect

    def on_click(self, event):
        """Handle mouse click"""
        # Save state before making changes
        self.save_state()
        self.is_dragging = True
        self.interact_pixel(event)

    def on_drag(self, event):
        """Handle mouse drag"""
        if self.is_dragging:
            self.interact_pixel(event)

    def on_release(self, event):
        """Handle mouse release"""
        self.is_dragging = False

    def on_hover(self, event):
        """Show pixel coordinates on hover"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        display_c = int(canvas_x // self.pixel_size)
        display_r = int(canvas_y // self.pixel_size)

        display_rows = NUM_ROWS // self.scale
        display_cols = ROW_WIDTH // self.scale

        if 0 <= display_r < display_rows and 0 <= display_c < display_cols:
            # Convert to actual DMD coordinates
            actual_r = display_r * self.scale
            actual_c = display_c * self.scale
            pixel_val = self.pixel_array[actual_r, actual_c]
            state = "On" if pixel_val == 1 else "Off"
            self.hover_label.config(text=f"Row: {actual_r}, Col: {actual_c} ({state})")
        else:
            self.hover_label.config(text="")

    def interact_pixel(self, event):
        """Toggle or paint pixels based on mode"""
        # Convert to canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        display_c = int(canvas_x // self.pixel_size)
        display_r = int(canvas_y // self.pixel_size)

        display_rows = NUM_ROWS // self.scale
        display_cols = ROW_WIDTH // self.scale

        if 0 <= display_r < display_rows and 0 <= display_c < display_cols:
            mode = self.draw_mode.get()
            brush = self.brush_size.get()

            # Apply to brush area
            for dr in range(-brush + 1, brush):
                for dc in range(-brush + 1, brush):
                    brush_r = display_r + dr
                    brush_c = display_c + dc

                    if 0 <= brush_r < display_rows and 0 <= brush_c < display_cols:
                        # Update all pixels in the scaled region
                        for sr in range(self.scale):
                            for sc in range(self.scale):
                                actual_r = brush_r * self.scale + sr
                                actual_c = brush_c * self.scale + sc
                                if actual_r < NUM_ROWS and actual_c < ROW_WIDTH:
                                    if mode == "toggle":
                                        self.pixel_array[actual_r, actual_c] = 1 - self.pixel_array[actual_r, actual_c]
                                    elif mode == "paint":
                                        self.pixel_array[actual_r, actual_c] = 1  # On (black)
                                    elif mode == "erase":
                                        self.pixel_array[actual_r, actual_c] = 0  # Off (white)

                        # Update display
                        if (brush_r, brush_c) in self.rects:
                            val = self.pixel_array[brush_r * self.scale, brush_c * self.scale]
                            color = 'black' if val == 1 else 'white'
                            self.canvas.itemconfig(self.rects[(brush_r, brush_c)], fill=color)

    def apply_pattern(self, pattern_type):
        """Apply quick patterns"""
        self.save_state()
        half = NUM_ROWS // 2

        if pattern_type == "top_white":
            self.pixel_array[:half, :] = 0
        elif pattern_type == "top_black":
            self.pixel_array[:half, :] = 1
        elif pattern_type == "bottom_white":
            self.pixel_array[half:, :] = 0
        elif pattern_type == "bottom_black":
            self.pixel_array[half:, :] = 1

        self.draw_grid()

    def clear_all(self):
        """Set all pixels to white"""
        self.save_state()
        self.pixel_array.fill(0)
        self.draw_grid()

    def fill_all(self):
        """Set all pixels to black"""
        self.save_state()
        self.pixel_array.fill(1)
        self.draw_grid()

    def zoom_in(self):
        """Zoom in - increase pixel size"""
        if self.pixel_size < 20:
            self.pixel_size += 2
            self.draw_grid()
            self.update_scroll_region()
            self.update_info_label()

    def zoom_out(self):
        """Zoom out - decrease pixel size"""
        if self.pixel_size > 2:
            self.pixel_size -= 2
            self.draw_grid()
            self.update_scroll_region()
            self.update_info_label()

    def save_bmp(self):
        """Save current pattern as BMP file"""
        try:
            # Ask user for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".bmp",
                filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")],
                initialfile="dmd_pattern.bmp"
            )

            if not filename:
                return  # User cancelled

            # Convert pixel_array to image
            # 0 = white (255), 1 = black (0)
            img_array = np.where(self.pixel_array == 0, 255, 0).astype(np.uint8)

            # Create and save image
            img = Image.fromarray(img_array, mode='L')
            img.save(filename)

            messagebox.showinfo("Success", f"Pattern saved to:\n{filename}")
            print(f"[INFO] Pattern saved to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save BMP:\n{str(e)}")
            print(f"[ERROR] {e}")

    def init_dmd(self):
        """Initialize DMD - exactly like running_dmd_diffpattern_2loaddata.py"""
        try:
            print("[INFO] Initializing DMD...")
            self.dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER,
                          row_width=ROW_WIDTH, num_rows=NUM_ROWS)

            # Use reset_clear_old() just like the working script!
            self.dmd.reset_clear_old()

            self.dmd_initialized = True
            self.status.config(text="DMD Ready", foreground="green")
            self.update_btn.config(state=tk.NORMAL)

            messagebox.showinfo("Success", "DMD initialized successfully!")
            print("[INFO] DMD ready for data loading.")
        except Exception as e:
            messagebox.showerror("Error", f"Init failed:\n{str(e)}")
            print(f"[ERROR] {e}")

    def update_display(self):
        """Update DMD - exactly like running_dmd_diffpattern_2loaddata.py with 2 batches"""
        if not self.dmd_initialized:
            messagebox.showwarning("Warning", "Initialize DMD first!")
            return

        try:
            print("[INFO] Loading pattern to DMD...")

            # Reset DMD to start position - CRITICAL!
            print("[INFO] Calling reset_clear_old()...")
            self.dmd.reset_clear_old()

            # Count black pixels for info
            black_pixels = np.sum(self.pixel_array)
            print(f"[INFO] Pattern has {black_pixels} black pixels out of {NUM_ROWS * ROW_WIDTH}")

            # BATCH 1: Top half (rows 0-383)
            BATCH_ROWS = NUM_ROWS // 2
            batch1 = bytearray()
            for row_idx in range(0, BATCH_ROWS):
                # Get this row's pixels
                pixel_row = self.pixel_array[row_idx, :].tolist()

                # Convert to bit-packed format
                row_data = create_bit_packed_row(pixel_row, row_width=ROW_WIDTH)
                batch1.extend(row_data)

            # Convert to ctypes array and load
            batch1_array = (ctypes.c_ubyte * len(batch1))(*batch1)
            self.dmd.load_row(batch1_array)
            self.dmd.load_control()
            print(f"[INFO] Batch 1 loaded (rows 0-{BATCH_ROWS-1})")

            # BATCH 2: Bottom half (rows 384-767)
            batch2 = bytearray()
            for row_idx in range(BATCH_ROWS, NUM_ROWS):
                # Get this row's pixels
                pixel_row = self.pixel_array[row_idx, :].tolist()

                # Convert to bit-packed format
                row_data = create_bit_packed_row(pixel_row, row_width=ROW_WIDTH)
                batch2.extend(row_data)

            # Convert to ctypes array and load
            batch2_array = (ctypes.c_ubyte * len(batch2))(*batch2)
            self.dmd.load_row(batch2_array)
            print(f"[INFO] Batch 2 loaded (rows {BATCH_ROWS}-{NUM_ROWS-1})")

            # Call reset_clear to display - just like the working script!
            print("[INFO] Calling reset_clear() to display...")
            self.dmd.reset_clear()

            print("[INFO] DMD updated successfully!")
            messagebox.showinfo("Success", f"Display updated!\n{black_pixels} black pixels")

        except Exception as e:
            messagebox.showerror("Error", f"Update failed:\n{str(e)}")
            print(f"[ERROR] {e}")


def main():
    root = tk.Tk()
    app = EnhancedDMDGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
