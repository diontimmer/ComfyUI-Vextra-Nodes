import torch
import numpy as np
import platform
from PIL import Image, ImageDraw, ImageFont

class FontText():
    """
    This node provides a simple interface to add text to the output image.
    """
    def __init__(self):
        # Added code by Aegis72 to autosense OS and supply a proper default font for Mac and Linux users 
        # Detect the operating system
        self.os_name = platform.system()
        
        # Set default font path based on the operating system
        if self.os_name == 'Windows':
            self.default_font_path = 'C:/Windows/Fonts/arial.ttf'
        elif self.os_name == 'Darwin':  # macOS
            self.default_font_path = '/System/Library/Fonts/SFNS.ttf'  # San Francisco is the default font for macOS
        elif self.os_name == 'Linux':
            self.default_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Common path for a default font in Linux
        else:
            self.default_font_path = ''  # Fallback path if OS is not recognized

    @classmethod
    def INPUT_TYPES(cls):
        """
        Input Types
        """
        # Use the instance's default font path
        default_font_path = cls().default_font_path
        return {
            "required": {
                "images": ("IMAGE",),},
            "optional": {
                "font_ttf": ("STRING", {"default": default_font_path}),
                # The rest of the parameters remain unchanged
                "size": ("INT", {"default": 50, "min": 2, "max": 1000, "step": 1}),
                "x": ("INT", {"default": 50, "min": 2, "max": 10000, "step": 1}),
                "y": ("INT", {"default": 50, "min": 2, "max": 10000, "step": 1}),
                "text": ("STRING", {"default": "Hello World", "multiline": True}),
                "color": ("STRING", {"default": 'rgba(255, 255, 255, 255)'}),
                "anchor": (["Bottom Left Corner", "Center"],),
                "rotate": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 0.1}),
                "color_mode": (["RGB", "RGBA"],),
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

    def do_font(self, images, font_ttf, size, x, y, color, anchor, rotate, color_mode, text):
        #create empty tensor with the same shape as images
        total_images = []
        center_anchor = True if anchor == 'Center' else False
        if color.startswith('#'):
            color_rgba = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            color_rgba = tuple(map(int, color.strip('rgba()').split(',')))
        for image in images:
            image = self.tensor_to_pil(image)
            
            add_text_to_image(image, font_ttf, size, x, y, text, color_rgba, center_anchor, rotate)

            # convert to tensor
            out_image = np.array(image.convert(color_mode)).astype(np.float32) / 255.0
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