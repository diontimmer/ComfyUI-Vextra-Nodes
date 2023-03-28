import torch
import numpy as np
from PIL import Image
class Flatten_Colors():
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
                "number_of_colors": ("INT", {"default": 5, "min": 1, "max": 4000, "step": 1}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "flatten"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def flatten(self, images, number_of_colors):
        #create empty tensor with the same shape as images
        total_images = []
        for image in images:
            image = self.tensor_to_pil(image)
            image = image.convert('P', palette=Image.ADAPTIVE, colors=number_of_colors)
            
            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)


NODE_CLASS_MAPPINGS = {
    "Flatten Colors": Flatten_Colors
}