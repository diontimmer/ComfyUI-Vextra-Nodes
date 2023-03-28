import torch
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class FontText():
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
                "font_ttf": ("STRING", {"default": 'C:/Windows/Fonts/arial.ttf'}),
                "size": ("INT", {"default": 50, "min": 2, "max": 1000, "step": 1}),
                "x": ("INT", {"default": 50, "min": 2, "max": 10000, "step": 1}),
                "y": ("INT", {"default": 50, "min": 2, "max": 10000, "step": 1}),
                "text": ("STRING", {"default": "Hello World"}),
                "color": ("STRING", {"default": 'rgb(255, 255, 255)'}),
                "anchor": (["Bottom Left Corner", "Center"],),
                "rotate": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 0.1}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_font"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def do_font(self, images, font_ttf, size, x, y, text, color, anchor, rotate):
        #create empty tensor with the same shape as images
        total_images = []
        center_anchor = True if anchor == 'Center' else False
        if color.startswith('#'):
            color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_rgb = tuple(map(int, color.strip('rgb()').split(',')))
        for image in images:
            image = self.tensor_to_pil(image)
            
            add_text_to_image(image, font_ttf, size, x, y, text, color_rgb, center_anchor, rotate)






            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

NODE_CLASS_MAPPINGS = {
    "Add Text To Image": FontText
}

def add_text_to_image(img, font_ttf, size, x, y, text, color_rgb, center=False, rotate=0):
    draw = ImageDraw.Draw(img)
    myFont = ImageFont.truetype(font_ttf, size)
    text_width, text_height = draw.textsize(text, font=myFont)

    if center:
        x -= text_width // 2
        y -= text_height // 2

    if rotate != 0:
        text_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((x, y), text, font=myFont, fill=color_rgb)
        text_img = text_img.rotate(rotate, resample=Image.BICUBIC, expand=True)
        img.paste(text_img, (0, 0), text_img)
    else:
        draw.text((x, y), text, font=myFont, fill=color_rgb)

    return img
