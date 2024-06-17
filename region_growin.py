import numpy as np
from PyQt5.QtCore import Qt

def region_growing(image, seed, threshold):
    height, width = image.shape[:2]
    segmented = np.zeros((height, width), np.uint8)
    seed_value = image[seed[1], seed[0]]
    pixels = [seed]
    while pixels:
        x, y = pixels.pop(0)
        if segmented[y, x] == 0:
            segmented[y, x] = 255
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and segmented[ny, nx] == 0:
                    if abs(int(image[ny, nx]) - int(seed_value)) < threshold:
                        pixels.append((nx, ny))
    return segmented
