import torch
import numpy as np
from PIL import Image
import subprocess
import sys
try:
    import pilgram
except ModuleNotFoundError:
    # install pixelsort in current venv
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pilgram"])
    import pilgram

class ApplyFilter():

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
                "instagram_filter": ([
                        "_1977",
                        "aden",
                        "brannan",
                        "brooklyn",
                        "clarendon",
                        "earlybird",
                        "gingham",
                        "hudson",
                        "inkwell",
                        "kelvin",
                        "lark",
                        "lofi",
                        "maven",
                        "mayfair",
                        "moon",
                        "nashville",
                        "perpetua",
                        "reyes",
                        "rise",
                        "slumber",
                        "stinson",
                        "toaster",
                        "valencia",
                        "walden",
                        "willow",
                        "xpro2",
                            ],),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_filter"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def apply_filter(self, images, instagram_filter):
        #create empty tensor with the same shape as images
        total_images = []
        filter_fn = getattr(pilgram, instagram_filter)
        for image in images:
            image = self.tensor_to_pil(image)
            image = filter_fn(image)

            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "Apply Instagram Filter": ApplyFilter,
}
