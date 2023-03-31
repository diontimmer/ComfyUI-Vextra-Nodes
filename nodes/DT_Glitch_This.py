import torch
import numpy as np
from PIL import Image
import subprocess
import sys
try:
    from glitch_this import ImageGlitcher
except ModuleNotFoundError:
    # install pixelsort in current venv
    subprocess.check_call([sys.executable, "-m", "pip", "install", "glitch-this"])
    from glitch_this import ImageGlitcher

class GlitchThis():

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
                "glitch_amount": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.01}),
                "color_offset": (['Disable', 'Enable'],),
                "scan_lines": (['Disable', 'Enable'],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_glitch"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def string2bool(self, v):
        return v == 'Enable'

    def apply_glitch(self, images, glitch_amount=1, color_offset='Disable', scan_lines='Disable', seed=0):
        color_offset = self.string2bool(color_offset)
        scan_lines = self.string2bool(scan_lines)
        glitcher = ImageGlitcher()
        #create empty tensor with the same shape as images
        total_images = []
        for image in images:
            image = self.tensor_to_pil(image)
            image = glitcher.glitch_image(image, glitch_amount, color_offset=color_offset, scan_lines=scan_lines, seed=seed)

            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "GlitchThis Effect": GlitchThis,
}
