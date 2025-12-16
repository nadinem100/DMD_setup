import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import numpy as np
from dmd_dll_class import DMD

# Constants
DLL_PATH = r"C:\Windows\SysWOW64\D4100_usb.dll"
DEVICE_NUMBER = 0
ROW_WIDTH = 1024
NUM_ROWS = 768

class DMDPixelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DMD Pixel Controller")

        # Display resolution (we'll show a scaled down version)
        self.display_scale = 8  # Show every Nth pixel
        self.display_width = ROW_WIDTH // self.display_scale
        self.display_height = NUM_ROWS // self.display_scale

        # Pixel display size (how large each pixel appears on screen)
        self.pixel_display_size = 10  # Start with 10 pixels, adjustable

        # Pixel state array (1 = black/mirror off, 0 = white/mirror on)
        self.pixel_array = np.zeros((NUM_ROWS, ROW_WIDTH), dtype=np.uint8)

        # Initialize DMD
        self.dmd = None
        self.dmd_initialized = False

        # Setup GUI
        self.setup_gui()

    def setup_gui(self):
        # Control panel frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initialize DMD button
        self.init_button = ttk.Button(control_frame, text="Initialize DMD", command=self.initialize_dmd)
        self.init_button.grid(row=0, column=0, padx=5, pady=5)

        # Update DMD button
        self.update_button = ttk.Button(control_frame, text="Update DMD Display",
                                       command=self.update_dmd, state=tk.DISABLED)
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        # Clear DMD hardware button
        self.clear_dmd_button = ttk.Button(control_frame, text="Clear DMD Hardware",
                                          command=self.clear_dmd_hardware, state=tk.DISABLED)
        self.clear_dmd_button.grid(row=0, column=2, padx=5, pady=5)

        # Clear all button
        self.clear_button = ttk.Button(control_frame, text="Clear All Pixels", command=self.clear_all)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5)

        # Fill all button
        self.fill_button = ttk.Button(control_frame, text="Fill All Pixels", command=self.fill_all)
        self.fill_button.grid(row=0, column=4, padx=5, pady=5)

        # Status label
        self.status_label = ttk.Label(control_frame, text="DMD not initialized",
                                     foreground="red")
        self.status_label.grid(row=0, column=4, padx=20, pady=5)

        # Info label
        info_text = f"Display: {self.display_width}x{self.display_height} (1:{self.display_scale} scale)\nActual DMD: {ROW_WIDTH}x{NUM_ROWS}"
        info_label = ttk.Label(control_frame, text=info_text, font=('Arial', 8))
        info_label.grid(row=1, column=0, columnspan=5, pady=5)

        # Zoom controls
        zoom_frame = ttk.LabelFrame(control_frame, text="Zoom Controls", padding="5")
        zoom_frame.grid(row=3, column=0, columnspan=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(zoom_frame, text="Pixel Size:").grid(row=0, column=0, padx=5)
        self.zoom_var = tk.IntVar(value=self.pixel_display_size)
        zoom_scale = ttk.Scale(zoom_frame, from_=2, to=30, variable=self.zoom_var,
                              orient=tk.HORIZONTAL, command=self.on_zoom_change, length=200)
        zoom_scale.grid(row=0, column=1, padx=5)
        self.zoom_label = ttk.Label(zoom_frame, text=f"{self.pixel_display_size}px")
        self.zoom_label.grid(row=0, column=2, padx=5)

        ttk.Button(zoom_frame, text="Fit to Window", command=self.fit_to_window).grid(row=0, column=3, padx=10)

        # Drawing mode controls
        mode_frame = ttk.LabelFrame(control_frame, text="Drawing Mode", padding="5")
        mode_frame.grid(row=2, column=0, columnspan=5, pady=5, sticky=(tk.W, tk.E))

        self.draw_mode = tk.StringVar(value="single")
        ttk.Radiobutton(mode_frame, text="Single Pixel", variable=self.draw_mode,
                       value="single").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text="Paint (Drag)", variable=self.draw_mode,
                       value="paint").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(mode_frame, text="Erase (Drag)", variable=self.draw_mode,
                       value="erase").grid(row=0, column=2, padx=5)

        # Brush size for paint/erase
        ttk.Label(mode_frame, text="Brush Size:").grid(row=0, column=3, padx=(20, 5))
        self.brush_size = tk.IntVar(value=1)
        brush_spinbox = ttk.Spinbox(mode_frame, from_=1, to=20, textvariable=self.brush_size,
                                   width=5)
        brush_spinbox.grid(row=0, column=4, padx=5)

        # Canvas frame
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Make canvas frame expandable
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        # Create canvas with scrollbars
        self.canvas_width = 1200
        self.canvas_height = 800
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width,
                               height=self.canvas_height, bg='white')

        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Update scroll region
        self.update_scroll_region()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.is_dragging = False

        # Draw initial grid
        self.draw_grid()

    def update_scroll_region(self):
        """Update the canvas scroll region based on current pixel size"""
        total_width = self.display_width * self.pixel_display_size
        total_height = self.display_height * self.pixel_display_size
        self.canvas.configure(scrollregion=(0, 0, total_width, total_height))

    def on_zoom_change(self, value):
        """Handle zoom slider change"""
        new_size = int(float(value))
        self.pixel_display_size = new_size
        self.zoom_label.config(text=f"{new_size}px")
        self.update_scroll_region()
        self.draw_grid()

    def fit_to_window(self):
        """Adjust pixel size to fit the display in the current window"""
        # Get current canvas dimensions
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate pixel size to fit
        size_for_width = max(1, canvas_width // self.display_width)
        size_for_height = max(1, canvas_height // self.display_height)
        optimal_size = min(size_for_width, size_for_height)

        self.zoom_var.set(optimal_size)
        self.pixel_display_size = optimal_size
        self.zoom_label.config(text=f"{optimal_size}px")
        self.update_scroll_region()
        self.draw_grid()

    def draw_grid(self):
        """Draw the pixel grid on canvas"""
        self.canvas.delete("all")
        self.pixel_rects = {}

        for row in range(self.display_height):
            for col in range(self.display_width):
                x1 = col * self.pixel_display_size
                y1 = row * self.pixel_display_size
                x2 = x1 + self.pixel_display_size
                y2 = y1 + self.pixel_display_size

                # Get actual pixel state (average over the scaled region)
                actual_row = row * self.display_scale
                actual_col = col * self.display_scale
                pixel_value = self.pixel_array[actual_row, actual_col]

                color = 'black' if pixel_value == 1 else 'white'
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill=color, outline='gray')
                self.pixel_rects[(row, col)] = rect

    def on_canvas_click(self, event):
        """Handle canvas click"""
        self.is_dragging = True
        self.handle_pixel_interaction(event)

    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.is_dragging:
            self.handle_pixel_interaction(event)

    def handle_pixel_interaction(self, event):
        """Toggle or paint pixels based on mode"""
        # Convert canvas coordinates to grid coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        col = int(canvas_x // self.pixel_display_size)
        row = int(canvas_y // self.pixel_display_size)

        if 0 <= row < self.display_height and 0 <= col < self.display_width:
            mode = self.draw_mode.get()
            brush = self.brush_size.get()

            # Apply to actual pixel array (with scaling)
            for dr in range(-brush + 1, brush):
                for dc in range(-brush + 1, brush):
                    display_r = row + dr
                    display_c = col + dc

                    if 0 <= display_r < self.display_height and 0 <= display_c < self.display_width:
                        actual_row_start = display_r * self.display_scale
                        actual_col_start = display_c * self.display_scale

                        # Update the entire scaled region
                        for ar in range(self.display_scale):
                            for ac in range(self.display_scale):
                                r_idx = actual_row_start + ar
                                c_idx = actual_col_start + ac
                                if r_idx < NUM_ROWS and c_idx < ROW_WIDTH:
                                    if mode == "single":
                                        # Toggle
                                        self.pixel_array[r_idx, c_idx] = 1 - self.pixel_array[r_idx, c_idx]
                                    elif mode == "paint":
                                        self.pixel_array[r_idx, c_idx] = 1  # Black
                                    elif mode == "erase":
                                        self.pixel_array[r_idx, c_idx] = 0  # White

                        # Update display
                        if (display_r, display_c) in self.pixel_rects:
                            pixel_value = self.pixel_array[actual_row_start, actual_col_start]
                            color = 'black' if pixel_value == 1 else 'white'
                            self.canvas.itemconfig(self.pixel_rects[(display_r, display_c)],
                                                 fill=color)

    def initialize_dmd(self):
        """Initialize the DMD device"""
        try:
            self.dmd = DMD(DLL_PATH, device_number=DEVICE_NUMBER,
                          row_width=ROW_WIDTH, num_rows=NUM_ROWS)
            # Use reset_clear_old() like the working script does!
            self.dmd.reset_clear_old()

            self.dmd_initialized = True
            self.status_label.config(text="DMD Initialized", foreground="green")
            self.update_button.config(state=tk.NORMAL)
            self.clear_dmd_button.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "DMD initialized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize DMD:\n{str(e)}")
            self.status_label.config(text="DMD initialization failed", foreground="red")

    def clear_dmd_hardware(self):
        """Clear the DMD hardware (reset it to blank/white)"""
        if not self.dmd_initialized:
            messagebox.showwarning("Warning", "Please initialize DMD first!")
            return

        try:
            self.dmd.reset_clear()
            messagebox.showinfo("Success", "DMD hardware cleared!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear DMD:\n{str(e)}")

    def update_dmd(self):
        """Send current pixel pattern to DMD (matches working script exactly)"""
        if not self.dmd_initialized:
            messagebox.showwarning("Warning", "Please initialize DMD first!")
            return

        try:
            # Check what we're loading
            total_pixels = np.sum(self.pixel_array)
            print(f"[DEBUG] Updating DMD with {total_pixels} black pixels out of {NUM_ROWS * ROW_WIDTH}")

            # Just load all rows - no setup needed! (matching running_dmd_diffpattern_2loaddata.py)
            print("[DEBUG] Loading all 768 rows...")
            for row_idx in range(NUM_ROWS):
                # Get pixel array for this row
                pixel_row = self.pixel_array[row_idx, :].tolist()

                # Convert to bit-packed format
                row_data = self.create_bit_packed_row(pixel_row)

                # Debug first row
                if row_idx == 0:
                    print(f"[DEBUG] Row 0 first 16 bytes: {list(row_data[:16])}")

                # Load to DMD
                uchar_array = (ctypes.c_ubyte * ROW_WIDTH)(*row_data)
                self.dmd.load_row(uchar_array)

            # Call reset_clear to display the loaded data (matching the working script!)
            print("[DEBUG] Calling reset_clear() to display loaded data...")
            self.dmd.reset_clear()

            print("[DEBUG] DMD update complete!")
            messagebox.showinfo("Success", "DMD display updated!")
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            messagebox.showerror("Error", f"Failed to update DMD:\n{str(e)}")

    def create_bit_packed_row(self, pixel_array):
        """Convert pixel array to bit-packed byte array"""
        packed_bytes = bytearray()

        for i in range(0, ROW_WIDTH, 8):
            byte = 0
            for bit in range(8):
                if i + bit < ROW_WIDTH:
                    byte |= (pixel_array[i + bit] << (7 - bit))
            packed_bytes.append(byte)

        return packed_bytes

    def clear_all(self):
        """Clear all pixels (set to white/on)"""
        self.pixel_array.fill(0)
        self.draw_grid()

    def fill_all(self):
        """Fill all pixels (set to black/off)"""
        self.pixel_array.fill(1)
        self.draw_grid()


def main():
    root = tk.Tk()
    app = DMDPixelGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
