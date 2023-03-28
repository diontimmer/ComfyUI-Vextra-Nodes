import torch
import numpy as np
from PIL import Image

COLOR_MODES = {
    'RGB': 'RGB',
    'RGBA': 'RGBA',
    'luminance': 'L',
    'luminance_alpha': 'LA',
    'cmyk': 'CMYK',
    'ycbcr': 'YCbCr',
    'lab': 'LAB',
    'hsv': 'HSV',
    'single_channel': '1',
}

class Swap_Color_Mode():
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
                "color_mode": (['default', 'luminance', 'single_channel'],),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_swap"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def do_swap(self, images, color_mode='default'):
        #create empty tensor with the same shape as images
        total_images = []
        for image in images:
            image = self.tensor_to_pil(image)
            if color_mode != 'default':
                correct_color_mode = COLOR_MODES[color_mode]
                image = image.convert(correct_color_mode)
            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "Swap Color Mode": Swap_Color_Mode
}