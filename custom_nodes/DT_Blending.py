import torch
import numpy as np
from PIL import Image
import subprocess
import sys
try:
    import blend_modes
except ModuleNotFoundError:
    # install pixelsort in current venv
    subprocess.check_call([sys.executable, "-m", "pip", "install", "blend-modes"])
    import blend_modes

class Blend():

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Input Types
        """
        return {
            "required": {
                "images_1": ("IMAGE",),
                "images_2": ("IMAGE",),},
            "optional": {
                "blend_mode": ([
                        "soft_light",
                        "lighten_only",
                        "dodge",
                        "addition",
                        "darken_only",
                        "multiply",
                        "hard_light",
                        "difference",
                        "subtract",
                        "grain_extract",
                        "grain_merge",
                        "divide",
                        "overlay",
                        "normal",
                            ],),
                "blend_opacity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_blend"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def hack_alpha_channel(self, pil_image): 
        # Create a new image with the same size and mode as the original image and fill it with opaque white
        new_image = Image.new('RGBA', pil_image.size, (255, 255, 255, 255))
        
        # Paste the original image onto the new image
        new_image.paste(pil_image, (0, 0))
        return new_image

    def apply_blend(self, images_1, images_2, blend_mode, blend_opacity):
        #create empty tensor with the same shape as images
        total_images = []
        blend_fn = getattr(blend_modes, blend_mode)
        if len(images_1) > len(images_2):
            raise Exception("BLEND: Second set of images cannot be less than the first set of images!")
        for i, image_1 in enumerate(images_1):
            image = self.tensor_to_pil(image_1)
            image = self.hack_alpha_channel(image)

            image_2 = self.tensor_to_pil(images_2[i])
            image_2 = self.hack_alpha_channel(image_2)

            if image.size != image_2.size:
                raise Exception("BLEND: Images must be the same size!")


            image = np.array(image)
            image = image.astype(float)

            image_2 = np.array(image_2)
            image_2 = image_2.astype(float)

            out_image = blend_fn(image, image_2, blend_opacity)
            out_image = Image.fromarray(out_image.astype(np.uint8))

            # convert to tensor
            out_image = np.array(out_image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)



NODE_CLASS_MAPPINGS = {
    "Blend": Blend,
}
