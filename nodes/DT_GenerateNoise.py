import torch
import numpy as np
from PIL import Image

def create_noise(mode='gaussian', scale=0.1, width=512, height=512):
    # Create empty image
    noise = np.zeros((height, width, 3), dtype=np.float32)

    if mode == 'gaussian':
        noise = np.random.normal(0, scale * 255, noise.shape).astype(np.float32)
    elif mode == 'uniform':
        noise = np.random.uniform(-scale * 255, scale * 255, noise.shape).astype(np.float32)
    elif mode == 'salt_and_pepper':
        salt = np.random.rand(*noise.shape[:2]) < scale / 2
        pepper = np.random.rand(*noise.shape[:2]) < scale / 2
        noise[..., 0] = np.where(salt, 255, 0)
        noise[..., 1] = np.where(pepper, 255, 0)
        noise[..., 2] = np.where(np.logical_not(salt | pepper), 255, 0)
    else:
        print(f'Unknown noise mode: {mode}')

    return Image.fromarray(noise.astype(np.uint8), 'RGB')


class NoiseImage():
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
                "mode": (['gaussian', 'uniform', 'salt_and_pepper'],),
                "noise_scale": ("FLOAT", {"default": 1, "min": 0.0, "max": 100.0, "step": 0.01}),
                "width": ("INT", {"default": 512, "min": 1, "max": 10000, "step": 1}),
                "height": ("INT", {"default": 512, "min": 1, "max": 10000, "step": 1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 10000, "step": 1}),
                },
            "optional": {
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_noise"

    CATEGORY = "VextraNodes"

    def do_noise(self, mode, noise_scale, width, height, batch_size):
        #create empty tensor with the same shape as images
        total_images = []
        for i in range(batch_size):
            image = create_noise(mode, noise_scale, width, height)
            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "Generate Noise Image": NoiseImage
}
