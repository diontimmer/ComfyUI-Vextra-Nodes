import torch
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class SolidColorImage():
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
                "width": ("INT", {"default": 512, "min": 64, "max": 10000, "step": 64}),
                "height": ("INT", {"default": 512, "min": 64, "max": 10000, "step": 64}),
                "color": ("STRING", {"default": 'rgb(255, 255, 255)'}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
                },
            "optional": {
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_solid"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def do_solid(self, width, height, color, batch_size):
        #create empty tensor with the same shape as images
        total_images = []
        if color.startswith('#'):
            color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_rgb = tuple(map(int, color.strip('rgb()').split(',')))
        for i in range(batch_size):
            image = Image.new('RGB', (width, height), color_rgb) 
            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "Create Solid Color": SolidColorImage
}
