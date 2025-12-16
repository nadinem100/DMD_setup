# DMD Single Site Addressing Control Software

Python-based control software for the Texas Instruments DMD (Digital Micromirror Device) used in single-site addressing experiments.

## Requirements

- **Python**: 32-bit Python (required for DMD DLL compatibility on Windows)
- **DLL**: `D4100_usb.dll` (should be in `C:\Windows\SysWOW64\`)
- **Hardware**: TI DMD connected via USB
- **Camera** (optional): Basler camera for feedback (requires separate camera control code)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nadinem100/DMD_setup.git
   cd DMD_setup
   ```

2. **Create a virtual environment** (use 32-bit Python on Windows):
   ```bash
   # On Windows with 32-bit Python
   python -m venv venv_32bit
   venv_32bit\Scripts\activate

   # On Mac/Linux (64-bit for testing, but DMD control needs Windows 32-bit)
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Main Scripts

### Core DMD Control
- **`running_dmd.py`**: Basic DMD control script
- **`dmd_dll_class.py`**: DMD class wrapper for DLL functions
- **`dmd_server.py`**: Server for 32-bit Python to control DMD (used by v2 scripts)

### Column Scan Experiments
- **`dmd_column_scan_v2.py`**: Latest column scan experiment (client-server architecture)
  - Uses 64-bit Python for camera/matplotlib
  - Communicates with 32-bit DMD server via files
  - Automatically turns off columns progressively and captures camera images

### GUI Tools
- **`dmd_gui_minimal.py`**: Minimal GUI for DMD control
- **`dmd_gui.py`**: Full-featured GUI with pattern loading

### Utilities
- **`visualize_pattern.py`**: Visualize DMD patterns
- **`turn_off_dmd.py`**: Utility to turn off all DMD pixels

## Usage Example

```python
from dmd_dll_class import DMD, create_bit_packed_row
import numpy as np

# Initialize DMD
dmd = DMD(r"C:\Windows\SysWOW64\D4100_usb.dll", device_number=0)
dmd.reset_clear_old()

# Create a pattern (768 rows x 1024 columns)
pattern = np.zeros((768, 1024), dtype=np.uint8)
pattern[300:400, 400:600] = 1  # Turn on a rectangular region

# Send pattern to DMD
# (see running_dmd.py for full example)
```

## Architecture Notes

### Client-Server Architecture (v2 scripts)
Due to Python bit-depth limitations:
- **32-bit Python**: Required for DMD DLL control (runs `dmd_server.py`)
- **64-bit Python**: Used for camera control and matplotlib (runs `dmd_column_scan_v2.py`)
- **Communication**: Via files (`dmd_command.txt`, `dmd_pattern.npy`, `dmd_status.txt`)

### DMD Pixel Encoding
- **0** = Mirror OFF (reflects light away) → appears WHITE on target
- **1** = Mirror ON (reflects light to target) → appears BLACK/DARK on target

## Troubleshooting

1. **DLL not found**: Ensure `D4100_usb.dll` is in `C:\Windows\SysWOW64\`
2. **Wrong Python bit-depth**: DMD control requires 32-bit Python on Windows
3. **Camera not found**: Check Basler camera drivers and path to `basler_camera.py`

## Directory Structure

- `/old_files/`: Archived experimental scripts and old implementations
- Root directory: Current working scripts

## Contributors

Nadine Meister - Endres Lab
