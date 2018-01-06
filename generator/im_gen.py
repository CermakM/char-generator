"""Generate character images for different fonts and stores them"""


import os
import sys

from PIL import Image, ImageDraw, ImageFont

# globals
CHARSET_SIZE = 0
# IMAGE_DIR = os.environ.get('PONCO_IMAGE_DIR')
# FONT_DIR = os.environ.get('PONCO_FONT_DIR')

FONT_DIR = '/home/macermak/code/thesis/char-generator/fonts'  # FIXME
IMAGE_DIR = 'images'  # FIXME

if not FONT_DIR or not IMAGE_DIR:
    print("FONT_DIR or IMAGE_DIR environment variable is missing", file=sys.stderr)
    exit(1)


def estimate_font_size(ttf, text, fit_size, font_size=20, eps=8):
    font = ImageFont.truetype(font=ttf, encoding='utf-8', size=font_size)

    w, h = font.getsize(text)
    _err = max(fit_size) - max(w, h)
    
    while abs(_err) > eps:
        w, h = font.getsize(text)
        _err = max(fit_size) - max(w, h)
        
        font_size += 1 if _err > 0 else -1
        font = ImageFont.truetype(font=ttf, encoding='utf-8', size=int(font_size))
    
    return font


def load_char_set() -> list:
    with open('charset.txt') as f:
        chars = f.read().split()

    global CHARSET_SIZE
    CHARSET_SIZE = len(chars)

    return chars


def load_font_set() -> list:
    import re
    fnames = []
    for root, _, files in os.walk(FONT_DIR):
        fnames.extend(os.path.join(root, f) for f in files if re.match(r'(.+)\.[odtfOTF]{3}', f))

    return fnames


def create_whiteboard(color='white', sample_size=(32, 32)) -> Image.Image:
    # a bit of a cheating here - charset size is 210 (15 x 14)
    bg_size = (15 * sample_size[0], 14 * sample_size[1])

    return Image.new(mode='RGBA', size=bg_size, color=color)


def create_fontboard(charset, fontset, sample_size=(32, 32)):
    from functools import reduce
    from numpy import subtract, floor_divide
    import random
    import re

    if not fontset:
        print("Empty argument provided: fontset - ", fontset, file=sys.stderr)

    board = create_whiteboard(sample_size=sample_size)

    for font_file in fontset:
        font_name = re.search(r"([^/]+)\.(\w)+$", font_file).group(1)
        board_name = "{path}/{ttf}-board.png".format(
                path=IMAGE_DIR,
                ttf=font_name)
        if os.path.isfile(board_name):
            print('Skipping', board_name)
            continue

        print("Creating board", board_name, "...") 
        font_board = board.copy()
        try:
            font = estimate_font_size(
                    ttf=font_file,
                    text='H',  # for sake of performance, assume that what works
                               # for H, works for everything else
                    fit_size=(32, 32),
                    eps=8
                    )
        except OSError as e:
            print("Skipping", font_file, e.args)
            continue

        draw = ImageDraw.Draw(font_board)

        init_pos = (0, 0)
        for char in charset:
            fo_x, fo_y = font.getoffset(char)
            # add a little bit of entropy
            font_offset = (
                    fo_x + random.randint(-3, 1),
                    fo_y + random.randint(1, 3))
            # location of char in a sample
            char_loc = reduce(subtract, (sample_size, font.size, font_offset))
            char_loc = floor_divide(char_loc, 2)
            # position of char on the board
            char_pos = init_pos + char_loc
            draw.text(
                    xy=char_pos,
                    text=char,
                    font=font,
                    fill="black"
                    )

            if init_pos[0] + sample_size[0] >= board.size[0]:
                init_pos = (0, init_pos[1] + sample_size[1])
            else:
                init_pos = (init_pos[0] + sample_size[0], init_pos[1])

        # save the board
        font_board.save(fp=board_name)
        print('Written', board_name)


def generate_char_images(charset, sample_size=(32, 32), *args, **kwargs):
    pass


if __name__ == '__main__':
    # check image directory
    if not os.path.isdir(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    # check fonts directory
    if not os.path.isdir(FONT_DIR):
        print("Missing 'fonts' directory", file=sys.stderr)
        exit(1)

    charset = load_char_set()
    fontset = load_font_set()
    im_size = (32, 32)

    create_fontboard(charset, fontset, sample_size=im_size)


