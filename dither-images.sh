# #!/usr/bin/env bash
# set -e

# # Rename this file to something more descriptive like 'dither-images.sh'

# # Create a random temp venv directory
# TEMP_VENV=$(mktemp -d venv.XXXX)
# python3 -m venv "$TEMP_VENV"
# source "$TEMP_VENV/bin/activate"

# # Install dependencies
# pip install -r requirements.txt

# # Run the dithering script
# python utils/dither_images.py --directory "$1"

# # Clean up
# deactivate
# rm -rf "$TEMP_VENV"

# TLDR, just run: 
python utils/dither_images.py --directory "$1"