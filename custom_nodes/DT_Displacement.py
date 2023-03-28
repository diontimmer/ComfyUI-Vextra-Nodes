import torch
import numpy as np
from PIL import Image

class Displacement_Map():
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
                "images": ("IMAGE",),
                "displacement_maps": ("IMAGE",),},
            "optional": {
                "scale": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 500.0, "step": 0.1}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_displace"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def do_displace(self, images, displacement_maps, scale):
        #create empty tensor with the same shape as images
        total_images = []

        if len(images) > len(displacement_maps):
            raise Exception("Number of images must be equal or less than the number of displacement maps!")

        for i, image in enumerate(images):
            displacement_map = displacement_maps[i]

            displacement_map = self.tensor_to_pil(displacement_map)
            image = self.tensor_to_pil(image)

            if displacement_map.size != image.size:
                raise Exception("Displacement map and image must be the same size!")

            image = apply_displacement_map(image, displacement_map, scale)
            

            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)



NODE_CLASS_MAPPINGS = {
    "Displacement Map": Displacement_Map
}

def apply_displacement_map(image, displacement_map, scale):
    # Convert PIL images to NumPy arrays
    image_array = np.array(image)
    displacement_map_array = np.array(displacement_map)

    # Get the dimensions of the image
    height, width, _ = image_array.shape

    # Calculate the displacement offsets based on the scale factor
    displacement_offsets = (displacement_map_array / 255 - 0.5) * scale

    # Create arrays for the X and Y coordinates of the pixels
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

    # Apply the displacement offsets to the X and Y coordinates
    x_displaced = (x_coords + displacement_offsets[..., 0]).clip(0, width - 1).astype(int)
    y_displaced = (y_coords + displacement_offsets[..., 1]).clip(0, height - 1).astype(int)

    # Create a new array with the same shape as the original image and copy the displaced pixels
    displaced_image_array = np.zeros_like(image_array)
    displaced_image_array[y_coords, x_coords] = image_array[y_displaced, x_displaced]

    # Convert the displaced image array back to a PIL image
    displaced_image = Image.fromarray(displaced_image_array)

    return displaced_image