from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from logic.game_logic import GameLogic
from processing.image_processor import ImageProcessor


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Spot the Difference")
        self.root.geometry("1280x780")

        self._processor = ImageProcessor()
        self._logic = GameLogic()

        self._click_tolerance = 16

        self._original = None
        self._modified = None
        self._current_path = None

        self._display_width = 600
        self._display_height = 600

        self._scale_x = 1
        self._scale_y = 1

        self._markers = []

        self._build_ui()

    def run(self):
        self.root.mainloop()

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self):
        # TOP BAR
        top = tk.Frame(self.root, pady=8)
        top.pack(fill=tk.X)

        btn_frame = tk.Frame(top)
        btn_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Load Image", width=12,
                  command=self.load_image, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Reset", width=10,
                  command=self.reset).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Reveal", width=10,
                  command=self.reveal, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)

        self.lbl = tk.Label(top, text="", font=("Segoe UI", 11, "bold"))
        self.lbl.pack(side=tk.RIGHT, padx=15)

        # LABELS
        label_frame = tk.Frame(self.root)
        label_frame.pack(fill=tk.X)

        tk.Label(label_frame, text="Original Image",
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, expand=True)

        tk.Label(label_frame, text="Modified Image (Click Here)",
                 font=("Segoe UI", 11, "bold")).pack(side=tk.RIGHT, expand=True)

        # LEGEND
        legend = tk.Label(
            self.root,
            text="Red = Found   |   Blue = Revealed   |   Click only on RIGHT image",
            fg="#555",
            font=("Segoe UI", 9)
        )
        legend.pack(pady=4)

        # CANVAS
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_left = tk.Canvas(frame, width=600, height=600, bg="#EDEDED")
        self.canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_right = tk.Canvas(frame, width=600, height=600, bg="#EDEDED")
        self.canvas_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_right.bind("<Button-1>", self.click)

    # -------------------------
    # LOAD
    # -------------------------
    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        self._current_path = path

        original, modified, regions = self._processor.load_and_generate(path)

        self._original = original
        self._modified = modified

        self._logic.set_differences(regions)
        self._markers.clear()

        self._prepare_scaled_images()
        self._render()

    def reset(self):
        if not self._current_path:
            messagebox.showinfo("Reset", "Load an image first.")
            return
        self.load_image()

    def reveal(self):
        if self._modified is None:
            return

        remaining = self._logic.reveal_remaining()
        for r in remaining:
            self._markers.append((r.x, r.y, r.radius, (255, 0, 0)))  # BLUE

        self._render()

    # -------------------------
    # SCALING
    # -------------------------
    def _prepare_scaled_images(self):
        h, w = self._original.shape[:2]

        scale = min(self._display_width / w, self._display_height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        self._scale_x = w / new_w
        self._scale_y = h / new_h

        self._disp_orig = cv2.resize(self._original, (new_w, new_h))
        self._disp_mod = cv2.resize(self._modified, (new_w, new_h))

    # -------------------------
    # CLICK
    # -------------------------
    def click(self, event):
        if self._modified is None:
            return

        # prevent clicking after game over
        if not self._logic.can_continue():
            return

        real_x = int(event.x * self._scale_x)
        real_y = int(event.y * self._scale_y)

        result = self._logic.process_click(real_x, real_y, self._click_tolerance)
        status = result["status"]

        if status in ["found", "win"]:
            r = result["region"]
            self._markers.append((r.x, r.y, r.radius, (0, 0, 255)))  # red

        if status == "lose":
            messagebox.showinfo("Game Over", "Too many mistakes!")

        if status == "win":
            messagebox.showinfo("Win", "All differences found!")

        self._render()

    # -------------------------
    # DRAW CENTERED
    # -------------------------
    def _draw_centered(self, canvas, image):
        canvas.delete("all")

        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()

        img_w = image.width()
        img_h = image.height()

        x = (canvas_w - img_w) // 2
        y = (canvas_h - img_h) // 2

        canvas.create_image(x, y, anchor="nw", image=image)

    # -------------------------
    # RENDER
    # -------------------------
    def _render(self):
        left = self._original.copy()
        right = self._modified.copy()

        for x, y, r, color in self._markers:
            cv2.circle(left, (x, y), r, color, 3, lineType=cv2.LINE_AA)
            cv2.circle(right, (x, y), r, color, 3, lineType=cv2.LINE_AA)

        self._prepare_scaled_images()

        self.tk_left = self._to_tk(self._disp_orig)
        self.tk_right = self._to_tk(self._disp_mod)

        self._draw_centered(self.canvas_left, self.tk_left)
        self._draw_centered(self.canvas_right, self.tk_right)

        self.lbl.config(
            text=f"Remaining: {self._logic.remaining_count()} | Mistakes: {self._logic.mistakes}"
        )

    def _to_tk(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return ImageTk.PhotoImage(Image.fromarray(img))