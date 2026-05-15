from __future__ import annotations

import random
from typing import Sequence, List, Tuple

import cv2
import numpy as np

from models.difference_region import DifferenceRegion


class ImageProcessor:
    """
    Handles OpenCV image loading, cloning, and random difference generation.
    """

    DIFFERENCE_TYPES: Sequence[str] = ("color_shift", "blur_region", "brightness_change")

    def __init__(self, target_difference_count: int = 5) -> None:
        self._target_difference_count = target_difference_count
        self.original_shape: Tuple[int, int, int] | None = None

    @property
    def target_difference_count(self) -> int:
        return self._target_difference_count

    # -------------------------
    # MAIN PIPELINE
    # -------------------------
    def load_and_generate(self, image_path: str):
        original = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if original is None:
            raise ValueError("Could not load image.")

        original = self._resize_for_display(original, max_dimension=1000)
        self.original_shape = original.shape

        modified = original.copy()

        regions = self._generate_regions(original.shape)

        for region in regions:
            if region.difference_type == "color_shift":
                self._apply_color_shift(modified, region)
            elif region.difference_type == "blur_region":
                self._apply_blur_region(modified, region)
            elif region.difference_type == "brightness_change":
                self._apply_brightness_change(modified, region)

        return original, modified, regions

    # -------------------------
    # RESIZE
    # -------------------------
    @staticmethod
    def _resize_for_display(image: np.ndarray, max_dimension: int = 1000) -> np.ndarray:
        h, w = image.shape[:2]
        scale = min(1.0, max_dimension / max(h, w))
        if scale == 1.0:
            return image
        return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # -------------------------
    # REGION GENERATION
    # -------------------------
    def _generate_regions(self, shape) -> List[DifferenceRegion]:
        h, w = shape[:2]
        min_side = min(h, w)

        min_radius = max(14, min_side // 30)
        max_radius = max(min_radius + 8, min_side // 18)

        regions: List[DifferenceRegion] = []
        attempts = 0
        max_attempts = 15000  # safer

        # Balanced distribution
        types_pool = list(self.DIFFERENCE_TYPES)
        random.shuffle(types_pool)

        while len(regions) < self._target_difference_count and attempts < max_attempts:
            attempts += 1

            radius = random.randint(min_radius, max_radius)

            x = random.randint(radius + 2, w - radius - 2)
            y = random.randint(radius + 2, h - radius - 2)

            diff_type = types_pool[len(regions) % len(types_pool)]

            candidate = DifferenceRegion(x, y, radius, diff_type)

            if all(not candidate.overlaps(r, padding=14) for r in regions):
                regions.append(candidate)

        if len(regions) != self._target_difference_count:
            raise ValueError("Image too small or too dense for generating differences.")

        return regions

    # -------------------------
    # EFFECTS
    # -------------------------
    def _apply_color_shift(self, image, region):
        x1, y1, x2, y2 = self._bounds(image, region)
        roi = image[y1:y2, x1:x2].copy()

        mask = self._mask(roi.shape[:2], region.x - x1, region.y - y1, region.radius)

        shifted = roi.astype(np.int16)

        # Slightly more natural variation
        shifts = [random.randint(-25, 25) for _ in range(3)]
        for i in range(3):
            shifted[:, :, i] = np.clip(shifted[:, :, i] + shifts[i], 0, 255)

        shifted = shifted.astype(np.uint8)

        alpha = (mask / 255.0)[:, :, None]
        blended = (roi * (1 - alpha) + shifted * alpha).astype(np.uint8)

        image[y1:y2, x1:x2] = blended

    def _apply_blur_region(self, image, region):
        x1, y1, x2, y2 = self._bounds(image, region)
        roi = image[y1:y2, x1:x2].copy()

        mask = self._mask(roi.shape[:2], region.x - x1, region.y - y1, region.radius)

        k = max(5, (region.radius // 2) * 2 + 1)
        blurred = cv2.GaussianBlur(roi, (k, k), 0)

        roi[mask == 255] = blurred[mask == 255]
        image[y1:y2, x1:x2] = roi

    def _apply_brightness_change(self, image, region):
        x1, y1, x2, y2 = self._bounds(image, region)
        roi = image[y1:y2, x1:x2].copy()

        mask = self._mask(roi.shape[:2], region.x - x1, region.y - y1, region.radius)

        beta = random.choice([-30, -25, 25, 30])
        adjusted = cv2.convertScaleAbs(roi, alpha=1.0, beta=beta)

        roi[mask == 255] = adjusted[mask == 255]
        image[y1:y2, x1:x2] = roi

    # -------------------------
    # HELPERS
    # -------------------------
    @staticmethod
    def _mask(shape, cx, cy, radius):
        mask = np.zeros(shape, dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 255, -1)
        return mask

    @staticmethod
    def _bounds(image, region):
        h, w = image.shape[:2]
        x1 = max(0, region.x - region.radius)
        y1 = max(0, region.y - region.radius)
        x2 = min(w, region.x + region.radius)
        y2 = min(h, region.y + region.radius)
        return x1, y1, x2, y2