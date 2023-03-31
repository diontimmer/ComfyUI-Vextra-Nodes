import os
import torchvision.transforms.functional as TF
from PIL import Image

class PictureIndex:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": ""}),
                "index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "doStuff"
    CATEGORY = "VextraNodes"

    def doStuff(self, path, index):
        if not os.path.exists(path):
            raise Exception("Path does not exist")
        images = []
        for image in os.listdir(path):
            if any(image.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                images.append(image)
        image = Image.open(os.path.join(path, images[index]))
        image = TF.to_tensor(image)
        print(image)



        return (image,)

NODE_CLASS_MAPPINGS = {
    "Load Picture Index": PictureIndex,
}