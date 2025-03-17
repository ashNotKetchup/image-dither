# Utilities

## Dithering

dither_images.py recursively traverses folders and creates dithered versions of the images it finds. These are stored in the same folder as the images in a folder called "dithers".

### Installation & Depedencies

depends on Pillow and hitherdither

`pip install Pillow git+https://www.github.com/hbldh/hitherdither`

### Usage:

Dither all the images found in the subdirectories of content `python3 utils/dither_images.py --directory src/content/`

Colorize the dithers as well based on the LTM categories: `python3 utils/dither_images.py --directory src/content/ --colorize`

Run the script with more debug output: `python3 utils/dither_images.py --directory src/content/ --colorize --verbose`

Remove all dithered files in the subdirectories of content: `python3 utils/dither_images.py --remove --directory content/`

Then: run script to replace all image references with dithered versions (markdown and html in md files) `python3 utils/replace_dither_links.py src/content`