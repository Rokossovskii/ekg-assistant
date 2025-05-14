import cv2
import numpy as np
import os


def preprocess_image(image_path, debug_dir=None):
    # Load and convert to grayscale
    original_image = load_image(image_path)
    save_debug_image(original_image, debug_dir, "01_original.png")

    # Remove grid
    grid_removed = remove_grid(original_image)
    save_debug_image(grid_removed, debug_dir, "02_grid_removed.png")

    # Clean up small noise
    clean_image = clean_and_normalize_signal(grid_removed)
    save_debug_image(clean_image, debug_dir, "03_cleaned.png")

    return clean_image, original_image


def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to load image from {image_path}")
    return to_grayscale(image)


def to_grayscale(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image.copy()


def remove_grid(image):
    kernel = np.ones((3, 3), np.uint8)
    morph_open = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    _, thresh = cv2.threshold(
        morph_open, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    return thresh


def clean_and_normalize_signal(image, min_size=5):
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        image, connectivity=8
    )

    cleaned = np.zeros_like(image)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            cleaned[labels == i] = 255

    if np.mean(cleaned) > 127:
        return cv2.bitwise_not(cleaned)
    return cleaned


def save_debug_image(image, output_dir, filename):
    if output_dir is not None:
        cv2.imwrite(os.path.join(output_dir, filename), image)
