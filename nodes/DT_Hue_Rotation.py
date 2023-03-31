import torch
import numpy as np
from PIL import Image
import math

def or_convert(im, mode):
    return im if im.mode == mode else im.convert(mode)

def hue_rotate(im, deg=0):
    cos_hue = math.cos(math.radians(deg))
    sin_hue = math.sin(math.radians(deg))

    matrix = [
        .213 + cos_hue * .787 - sin_hue * .213,
        .715 - cos_hue * .715 - sin_hue * .715,
        .072 - cos_hue * .072 + sin_hue * .928,
        0,
        .213 - cos_hue * .213 + sin_hue * .143,
        .715 + cos_hue * .285 + sin_hue * .140,
        .072 - cos_hue * .072 - sin_hue * .283,
        0,
        .213 - cos_hue * .213 - sin_hue * .787,
        .715 - cos_hue * .715 + sin_hue * .715,
        .072 + cos_hue * .928 + sin_hue * .072,
        0,
    ]

    rotated = or_convert(im, 'RGB').convert('RGB', matrix)
    return or_convert(rotated, im.mode)


class HueRotation():

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
                "hue_rotation": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 0.1}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_hr"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def apply_hr(self, images, hue_rotation):
        #create empty tensor with the same shape as images
        total_images = []
        for image in images:
            image = self.tensor_to_pil(image)
            image = hue_rotate(image, hue_rotation)
            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)






NODE_CLASS_MAPPINGS = {
    "Hue Rotation": HueRotation,
}
