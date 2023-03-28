# ComfyUI Vextra Nodes
 Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

## Installation
1. Install [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
2. Download nodes and place them in custom_nodes folder inside your ComfyUI installation.
3. Start/Restart ComfyUI

## Nodes

### Pixel Sort
Pixel sorting effect by [satyarth](https://github.com/satyarth/pixelsort). Will install pixelsort module upon installation.
Read about pixel sorting [here](http://satyarth.me/articles/pixel-sorting/).

### Swap Color Mode (Black & White)
Swap the color mode to luminescence or single channel, useful for making mask or simply making stuff black & white.

### Solid Color
Generates an empty solid color image with options for color, size and batch size.

### Chromatic Aberration
Chromatic Abarration adds a color shift to the image. Useful for making the image look more "analog".

### Add Text To Image
Supply the path to a .ttf file and add text to an image input. Has options for achor placement, rotation, color and more.

### Blending
Blending node that supports various blending modes. Uses [blend-modes](https://github.com/flrs/blend_modes) under the hood. Will install the module upon installation.

### Displacement
Displacement node that can distort an image using a supplied mask.

### Generate Noise
Generate various noises to use in masks or blending.

### Flatten Colors
Flatten the colors of an image to a variable amount of colors.

![alt text](https://i.imgur.com/PHLHp5m.png "Nodes Preview")<br>


## Citations
Pixel Sort by: [satyarth](https://github.com/satyarth)<br>
Blend Modes by: [flrs](https://github.com/flrs/)