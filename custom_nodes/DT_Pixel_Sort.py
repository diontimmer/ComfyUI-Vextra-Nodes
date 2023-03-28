import torch
import numpy as np
from PIL import Image
import sys
import subprocess
try:
    import pixelsort
except ModuleNotFoundError:
    # install pixelsort in current venv
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pixelsort"])
    import pixelsort


class Pixel_Sort:
    """
    This node provides a simple interface to apply PixelSort blur to the output image.
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Input Types
        """
        return {
            "required": {
                "images": ("IMAGE",),},
            "optional": {
                "character_length": ("INT", {"default": 50, "min": 2, "max": 1000, "step": 1}),
                "randomness": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "sorting_function": (["lightness", "hue", "saturation", "intensity", "minimum"],),
                "interval_function": (["threshold", "random", 'edges', 'waves', 'file', 'file-edges', 'none'],),
                "lower_threshold": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, "step": 0.01}),
                "upper_threshold": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "angle": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 0.1}),
                "mask_image": ("IMAGE", {"default": None}),
                "interval_image": ("IMAGE", {"default": None}),

            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_sort"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def do_sort(self, images, character_length, randomness, sorting_function, interval_function, lower_threshold, upper_threshold, angle, mask_image=None, interval_image=None, color_mode='default'):
        #create empty tensor with the same shape as images
        total_images = []
        for image in images:
            image = self.tensor_to_pil(image)
            mask_image = self.tensor_to_pil(mask_image)
            interval_image = self.tensor_to_pil(interval_image)
            out_image = pixelsort.pixelsort(
                image=image, 
                mask_image=mask_image, 
                interval_image=interval_image,
                randomness=randomness, 
                clength=character_length, 
                sorting_function=sorting_function, 
                interval_function=interval_function, 
                lower_threshold=lower_threshold, 
                upper_threshold=upper_threshold, 
                angle=angle)
            # convert to tensor
            out_image = np.array(out_image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "Pixel Sort": Pixel_Sort
}