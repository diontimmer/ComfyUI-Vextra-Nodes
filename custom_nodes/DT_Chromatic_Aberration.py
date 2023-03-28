import torch
import numpy as np
from PIL import Image
import math

class Chromatic_Aberration():
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
                "chromatic_strength": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                },
            }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "do_chromatic"

    CATEGORY = "VextraNodes"

    def tensor_to_pil(self, img):
        if img is not None:
            i = 255. * img.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def do_chromatic(self, images, chromatic_strength=0):
        #create empty tensor with the same shape as images
        total_images = []
        for image in images:
            image = self.tensor_to_pil(image)
            image = add_chromatic(image, chromatic_strength)
            # convert to tensor
            out_image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            out_image = torch.from_numpy(out_image).unsqueeze(0)
            total_images.append(out_image)


        total_images = torch.cat(total_images, 0)
        return (total_images,)

def add_chromatic(im, strength: float = 0):
    if strength == 0:
        return im
    r, g, b = im.split()
    rdata = np.asarray(r)
    rfinal = r
    gfinal = g
    bfinal = b

    # enlarge the green and blue channels slightly, blue being the most enlarged
    gfinal = gfinal.resize((round((1 + 0.018 * strength) * rdata.shape[1]),
                            round((1 + 0.018 * strength) * rdata.shape[0])), Image.ANTIALIAS)
    bfinal = bfinal.resize((round((1 + 0.044 * strength) * rdata.shape[1]),
                            round((1 + 0.044 * strength) * rdata.shape[0])), Image.ANTIALIAS)

    rwidth, rheight = rfinal.size
    gwidth, gheight = gfinal.size
    bwidth, bheight = bfinal.size
    rhdiff = (bheight - rheight) // 2
    rwdiff = (bwidth - rwidth) // 2
    ghdiff = (bheight - gheight) // 2
    gwdiff = (bwidth - gwidth) // 2

    # Centre the channels
    im = Image.merge("RGB", (
        rfinal.crop((-rwdiff, -rhdiff, bwidth - rwdiff, bheight - rhdiff)),
        gfinal.crop((-gwdiff, -ghdiff, bwidth - gwdiff, bheight - ghdiff)),
        bfinal))

    # Crop the image to the original image dimensions
    return im.crop((rwdiff, rhdiff, rwidth + rwdiff, rheight + rhdiff))



NODE_CLASS_MAPPINGS = {
    "Chromatic Aberration": Chromatic_Aberration
}


def cartesian_to_polar(data: np.ndarray) -> np.ndarray:
    """Returns the polar form of <data>
    """
    width = data.shape[1]
    height = data.shape[0]
    assert (width > 2)
    assert (height > 2)
    assert (width % 2 == 1)
    assert (height % 2 == 1)
    perimeter = 2 * (width + height - 2)
    halfdiag = math.ceil(((width ** 2 + height ** 2) ** 0.5) / 2)
    halfw = width // 2
    halfh = height // 2
    ret = np.zeros((halfdiag, perimeter, 3))

    # Don't want to deal with divide by zero errors...
    ret[0:(halfw + 1), halfh] = data[halfh, halfw::-1]
    ret[0:(halfw + 1), height + width - 2 +
                       halfh] = data[halfh, halfw:(halfw * 2 + 1)]
    ret[0:(halfh + 1), height - 1 + halfw] = data[halfh:(halfh * 2 + 1), halfw]
    ret[0:(halfh + 1), perimeter - halfw] = data[halfh::-1, halfw]

    # Divide the image into 8 triangles, and use the same calculation on
    # 4 triangles at a time. This is possible due to symmetry.
    # This section is also responsible for the corner pixels
    for i in range(0, halfh):
        slope = (halfh - i) / (halfw)
        diagx = ((halfdiag ** 2) / (slope ** 2 + 1)) ** 0.5
        unit_xstep = diagx / (halfdiag - 1)
        unit_ystep = diagx * slope / (halfdiag - 1)
        for row in range(halfdiag):
            ystep = round(row * unit_ystep)
            xstep = round(row * unit_xstep)
            if ((halfh >= ystep) and halfw >= xstep):
                ret[row, i] = data[halfh - ystep, halfw - xstep]
                ret[row, height - 1 - i] = data[halfh + ystep, halfw - xstep]
                ret[row, height + width - 2 +
                    i] = data[halfh + ystep, halfw + xstep]
                ret[row, height + width + height - 3 -
                    i] = data[halfh - ystep, halfw + xstep]
            else:
                break

    # Remaining 4 triangles
    for j in range(1, halfw):
        slope = (halfh) / (halfw - j)
        diagx = ((halfdiag ** 2) / (slope ** 2 + 1)) ** 0.5
        unit_xstep = diagx / (halfdiag - 1)
        unit_ystep = diagx * slope / (halfdiag - 1)
        for row in range(halfdiag):
            ystep = round(row * unit_ystep)
            xstep = round(row * unit_xstep)
            if (halfw >= xstep and halfh >= ystep):
                ret[row, height - 1 + j] = data[halfh + ystep, halfw - xstep]
                ret[row, height + width - 2 -
                    j] = data[halfh + ystep, halfw + xstep]
                ret[row, height + width + height - 3 +
                    j] = data[halfh - ystep, halfw + xstep]
                ret[row, perimeter - j] = data[halfh - ystep, halfw - xstep]
            else:
                break
    return ret


def polar_to_cartesian(data: np.ndarray, width: int, height: int) -> np.ndarray:
    """Returns the cartesian form of <data>.
    
    <width> is the original width of the cartesian image
    <height> is the original height of the cartesian image
    """
    assert (width > 2)
    assert (height > 2)
    assert (width % 2 == 1)
    assert (height % 2 == 1)
    perimeter = 2 * (width + height - 2)
    halfdiag = math.ceil(((width ** 2 + height ** 2) ** 0.5) / 2)
    halfw = width // 2
    halfh = height // 2
    ret = np.zeros((height, width, 3))

    def div0():
        # Don't want to deal with divide by zero errors...
        ret[halfh, halfw::-1] = data[0:(halfw + 1), halfh]
        ret[halfh, halfw:(halfw * 2 + 1)] = data[0:(halfw + 1),
                                            height + width - 2 + halfh]
        ret[halfh:(halfh * 2 + 1), halfw] = data[0:(halfh + 1), height - 1 + halfw]
        ret[halfh::-1, halfw] = data[0:(halfh + 1), perimeter - halfw]

    div0()

    # Same code as above, except the order of the assignments are switched
    # Code blocks are split up for easier profiling
    def part1():
        for i in range(0, halfh):
            slope = (halfh - i) / (halfw)
            diagx = ((halfdiag ** 2) / (slope ** 2 + 1)) ** 0.5
            unit_xstep = diagx / (halfdiag - 1)
            unit_ystep = diagx * slope / (halfdiag - 1)
            for row in range(halfdiag):
                ystep = round(row * unit_ystep)
                xstep = round(row * unit_xstep)
                if ((halfh >= ystep) and halfw >= xstep):
                    ret[halfh - ystep, halfw - xstep] = \
                        data[row, i]
                    ret[halfh + ystep, halfw - xstep] = \
                        data[row, height - 1 - i]
                    ret[halfh + ystep, halfw + xstep] = \
                        data[row, height + width - 2 + i]
                    ret[halfh - ystep, halfw + xstep] = \
                        data[row, height + width + height - 3 - i]
                else:
                    break

    part1()

    def part2():
        for j in range(1, halfw):
            slope = (halfh) / (halfw - j)
            diagx = ((halfdiag ** 2) / (slope ** 2 + 1)) ** 0.5
            unit_xstep = diagx / (halfdiag - 1)
            unit_ystep = diagx * slope / (halfdiag - 1)
            for row in range(halfdiag):
                ystep = round(row * unit_ystep)
                xstep = round(row * unit_xstep)
                if (halfw >= xstep and halfh >= ystep):
                    ret[halfh + ystep, halfw - xstep] = \
                        data[row, height - 1 + j]
                    ret[halfh + ystep, halfw + xstep] = \
                        data[row, height + width - 2 - j]
                    ret[halfh - ystep, halfw + xstep] = \
                        data[row, height + width + height - 3 + j]
                    ret[halfh - ystep, halfw - xstep] = \
                        data[row, perimeter - j]
                else:
                    break

    part2()

    # Repairs black/missing pixels in the transformed image
    def set_zeros():
        zero_mask = ret[1:-1, 1:-1] == 0
        ret[1:-1, 1:-1] = np.where(zero_mask, (ret[:-2, 1:-1] + ret[2:, 1:-1]) / 2, ret[1:-1, 1:-1])

    set_zeros()

    return ret