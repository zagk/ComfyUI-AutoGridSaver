import os
import folder_paths
from PIL import Image
import numpy as np

class AutoGridSaver:
    def __init__(self):
        self.images = []
        self.current_grid = 0

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "n_images": ("INT", {"default": 8, "min": 2, "max": 100, "step": 1}),
                "columns": ("INT", {"default": 4, "min": 1, "max": 20, "step": 1}),
                "filename_prefix": ("STRING", {"default": "AutoGrid"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_grid"
    OUTPUT_NODE = True
    CATEGORY = "image/AutoGrid"

    def save_grid(self, images, n_images, columns, filename_prefix, prompt=None, extra_pnginfo=None):

        # 이미지 누적
        if len(images.shape) == 4:
            for i in range(images.shape[0]):
                self.images.append(images[i:i+1])
        else:
            self.images.append(images)

        output_dir = folder_paths.get_output_directory()

        # 🔥 핵심: 가능한 만큼 계속 그리드 생성
        while len(self.images) >= n_images:

            grid_images = self.images[:n_images]
            rows = (n_images + columns - 1) // columns
            grid = self.make_image_grid(grid_images, columns, rows, n_images)

            # 파일 덮어쓰기 방지
            counter = self.current_grid
            while True:
                file_name = f"{filename_prefix}_grid_{counter:04d}.png"
                if not os.path.exists(os.path.join(output_dir, file_name)):
                    self.current_grid = counter
                    break
                counter += 1

            full_path = os.path.join(output_dir, file_name)
            grid.save(full_path)

            print(f"AutoGridSaver: {n_images} images grid saved -> {file_name} ({rows}x{columns})")

            # 🔥 사용한 것만 제거 (남은 건 유지)
            self.images = self.images[n_images:]
            self.current_grid += 1

        return ()

    def make_image_grid(self, images, columns, rows, n_images):
        sample = images[0].cpu().numpy().squeeze()

        if len(sample.shape) == 2:
            h, w = sample.shape
        else:
            h, w, _ = sample.shape

        grid_h = h * rows
        grid_w = w * columns
        grid_img = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

        for idx, img_tensor in enumerate(images):
            if idx >= n_images:
                break

            img = (img_tensor.cpu().numpy().squeeze() * 255).astype(np.uint8)

            if len(img.shape) == 3 and img.shape[2] == 4:
                img = img[:, :, :3]
            elif len(img.shape) == 2:
                img = np.stack([img]*3, axis=-1)

            row = idx // columns
            col = idx % columns

            grid_img[row*h:(row+1)*h, col*w:(col+1)*w] = img

        return Image.fromarray(grid_img)


NODE_CLASS_MAPPINGS = {"AutoGridSaver": AutoGridSaver}
NODE_DISPLAY_NAME_MAPPINGS = {"AutoGridSaver": "Auto Grid Saver zk"}