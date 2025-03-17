# image dithering script
# © 2022 Roel Roscam Abbing, released as AGPLv3
# see https://www.gnu.org/licenses/agpl-3.0.html
# Support your local low-tech magazine: https://solar.lowtechmagazine.com/donate.html 

import hitherdither
import os
import argparse
import shutil
from PIL import Image
import logging
from dotenv import load_dotenv
from PIL import ImageOps
from PIL import ImageEnhance

load_dotenv()  # Load environment variables from .env file

primary = os.getenv('PRIMARY')
secondary = os.getenv('SECONDARY')
background = os.getenv('BACKGROUND')
(primary,secondary,background)=(tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for hex in (primary,secondary,background) )



# create palette:

def interpolate_color(color1, color2, factor):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

def create_palette(colors, num_colors):
    palette = []
    n = len(colors) - 1
    for i in range(num_colors):
        segment = i / (num_colors - 1) * n
        idx = int(segment)
        factor = segment - idx
        c1 = colors[idx]
        c2 = colors[min(idx + 1, n)]
        palette.append(interpolate_color(c1, c2, factor))
    return palette


interp_palette = create_palette([primary,secondary,background],8)



parser = argparse.ArgumentParser(
    """
    This script recursively traverses folders and creates dithered versions of the images it finds.
    These are stored in the same folder as the images in a folder called "dithers".
    """
)

# parser.add_argument(
#     '-i', '--invert',
#     action='store_true',
#     help='Invert images before dithering'
# )

parser.add_argument(
    '-d', '--directory', help="Set the directory to traverse", default="." 
    )

parser.add_argument(
    '-rm', '--remove', help="Removes all the folders with dithers and their contents", action="store_true" 
    )

parser.add_argument(
    '-c', '--colorize', help="Colorizes the dithered images", action="store_true" 
    )

parser.add_argument(
    '-v', '--verbose', help="Print out more detailed information about what this script is doing", action="store_true" 
    )

args = parser.parse_args()

image_ext = [".jpg", ".JPG", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp"]


content_dir = args.directory

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

exclude_dirs = set(["dithers"])


logging.info("Dithering all images in {} and subfolders".format(content_dir))
logging.debug("excluding directories: {}".format("".join(exclude_dirs)))

def colorize(source_image, category):
    """
    Picks a colored dithering palette based on the post category.
    """

    colors = {
            'low-tech': hitherdither.palette.Palette([(30,32,40), (11,21,71),(57,77,174),(158,168,218),(187,196,230),(243,244,250)]),
            'obsolete': hitherdither.palette.Palette([(9,74,58), (58,136,118),(101,163,148),(144,189,179),(169,204,195),(242,247,246)]),
            'high-tech': hitherdither.palette.Palette([(86,9,6), (197,49,45),(228,130,124),(233,155,151),(242,193,190),(252,241,240)]),
            'grayscale': hitherdither.palette.Palette([(25,25,25), (75,75,75),(125,125,125),(175,175,175),(225,225,225),(250,250,250)])
        }


    if category:

        for i in colors.keys():
            if i in category.lower():
                color = colors[i]
                logging.info("Applying color palette '{}' for {}".format(i, category))
                break
            else:
                logging.info("No category for {}, {}".format(source_image, category))
                print("No category for {}, {}".format(source_image, category))
                color = colors['grayscale']

    else:
        logging.info("No category for {}, {}".format(source_image, category))
        print("No category for {}, {}".format(source_image, category))
        color = colors['grayscale']
        
    return color


def dither_image(source_image, output_image, category ='grayscale', invert=False):
    #see hitherdither docs for different dithering algos and settings

    if args.colorize:
        palette = colorize(source_image, category)
    else:
        palette = hitherdither.palette.Palette(interp_palette)

    try:
        img= Image.open(source_image).convert('RGB')
        if invert:
            img = ImageOps.invert(img)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(2)
        img.thumbnail((800,800), Image.LANCZOS)
        #palette = palettes[category]
        threshold = [96, 96, 96]
        img_dithered = hitherdither.ordered.bayer.bayer_dithering(img, palette, threshold, order=8) 
        #if args.colorize:
        #    img_dithered = colorize(img_dithered, category)
        #    logging.debug("Created {} in category {}".format(img_dithered, category))
            
        img_dithered.save(output_image, optimize=True)

    except Exception as e:
        logging.debug("❌ failed to convert {}".format(source_image))
        logging.debug(e)

def delete_dithers(content_dir):
    logging.info("Deleting 'dither' folders in {} and below".format(content_dir))
    for root, dirs, files in os.walk(content_dir, topdown=True):
        if root.endswith('dithers'):
            shutil.rmtree(root)
            logging.info("Removed {}".format(root))
        

def parse_front_matter(md):
    with open(md) as f:
        contents = f.readlines()
        cat = None
        for l in contents:
            if l.startswith("categories: "):
                cat = l.split("categories: ")[1]
                cat = cat.strip("[")
                cat = cat.strip()
                cat = cat.strip("]")

                logging.debug("Categories: {} from {}".format(cat, l.strip()))
        return cat

prev_root = None

# Store all dither directories created for final report
dither_directories = set()


for root, dirs, files in os.walk(os.path.abspath(content_dir), topdown=True):
    logging.debug("Checking next folder {}".format(root))
    print("Checking next folder {}".format(root))

    dirs[:] = [d for d in dirs if d not in exclude_dirs]

    category = None
    if prev_root is None:
        prev_root = root

    if prev_root is not root:
        if files:
            if any(x.endswith(tuple(image_ext)) for x in files):
                if not os.path.exists(os.path.join(root,'dithers')):
                    os.mkdir(os.path.join(root,'dithers'))
                    dither_directories.add(os.path.join(root,'dithers'))
                    logging.info("📁 created in {}".format(root))
                else:
                    dither_directories.add(os.path.join(root,'dithers'))
                    logging.debug("📁 already exists in {}".format(root))
            else: 
                logging.debug("No images in {}".format(root))
                print("No images in {}".format(root))
        else:
            logging.debug("No files in {}".format(root))
            print("No files in {}".format(root))
    else:
        logging.debug("Same folder as before")
        print("Same folder as before")
        print(prev_root)

    if args.colorize:
        #iterate over md files to find one with a category
        if not category:
            for i in os.listdir(root):
                if i.startswith('index'):
                    category2 = parse_front_matter(os.path.join(root,i))
                    
                    break


    for fname in files:
        if fname.endswith(tuple(image_ext)):
                # print(root)
                file_, ext = os.path.splitext(fname)
                source_image= os.path.join(root,fname)

                for inverted in [False, True]:
                    if inverted:
                        inverted_dir = os.path.join(root, 'dithers', 'inverted')
                        if not os.path.exists(inverted_dir):
                            os.makedirs(inverted_dir, exist_ok=True)
                        output_image = os.path.join(inverted_dir, file_+'.png')
                    else:
                        output_image = os.path.join(root, 'dithers', file_+'.png')
                    # if not os.path.exists(output_image): // Removed in order to allow colour change on compile
                    if not args.colorize:
                        category2 = "grayscale"
                    dither_image(source_image,output_image, category2, invert=inverted)
                    logging.info("🖼 converted {}".format(fname))
                    logging.debug(output_image)
                    # else:
                    #     logging.debug("Dithered version of {} found, skipping".format(fname))

    prev_root = root


logging.info("Done dithering")

# Add clear output about where to find the images
if dither_directories:
    print("\n=== Dithered images were saved to the following directories: ===")
    for directory in sorted(dither_directories):
        print(f"  📂 {directory}")
    print("\nUse 'open' command to view them directly: open [directory]")
else:
    print("\n⚠️ No dithered images were created. Make sure your input directory contains supported images.")
