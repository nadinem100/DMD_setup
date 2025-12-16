import numpy as np
from PIL import Image

# Constants
ROW_WIDTH = 1024
NUM_ROWS = 768
BATCH_ROWS = NUM_ROWS // 2  # 384

# Create the pattern array
pattern = np.zeros((NUM_ROWS, ROW_WIDTH), dtype=np.uint8)

# Batch 1 (Rows 0-383 - top half)
for row in range(0, BATCH_ROWS):
    # [1] * 100 + [0] * 200 + [1] * (ROW_WIDTH - 300)
    pattern[row, 0:100] = 1      # Black (100 pixels)
    pattern[row, 100:300] = 0    # White (200 pixels)
    pattern[row, 300:] = 1       # Black (remaining 724 pixels)

# Batch 2 (Rows 384-767 - bottom half)
white_pixels = 600
for row in range(BATCH_ROWS, NUM_ROWS):
    # [0] * 600 + [1] * (ROW_WIDTH - 600)
    pattern[row, 0:white_pixels] = 0     # White (600 pixels)
    pattern[row, white_pixels:] = 1      # Black (424 pixels)

# Convert to image (0=white=255, 1=black=0 for display)
# Note: In DMD terms, 1=black/mirror off, 0=white/mirror on
img_array = (1 - pattern) * 255  # Invert so 1->black(0) and 0->white(255)

# Create PIL Image
img = Image.fromarray(img_array.astype(np.uint8), mode='L')

# Save the image
output_path = "expected_dmd_pattern.png"
img.save(output_path)
print(f"Pattern visualization saved to: {output_path}")

# Also print some info
print("\nPattern description:")
print(f"Top half (rows 0-383):")
print(f"  - Black: 0-99 (100 pixels)")
print(f"  - White: 100-299 (200 pixels)")
print(f"  - Black: 300-1023 (724 pixels)")
print(f"\nBottom half (rows 384-767):")
print(f"  - White: 0-599 (600 pixels)")
print(f"  - Black: 600-1023 (424 pixels)")
