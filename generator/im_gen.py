"""Generate character images for different fonts and stores them"""


import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

# globals
CHARSET_SIZE = 0
IMAGE_DIR = os.environ.get('PONCO_IMAGE_DIR')
FONT_DIR = os.environ.get('PONCO_FONT_DIR')

if not FONT_DIR or not IMAGE_DIR:
    print("environment variable missing", file=sys.stderr)
    exit(1)

def get_correct_font(ttf, text, fit_size, font_size=20, eps=3):
    import math
    font = ImageFont.truetype(font=ttf, encoding='utf-8', size=font_size)

    w, h = font.getsize(text)
    _err = max(fit_size) - max(w, h)
    
    while _err > eps:  # FIXME
        w, h = font.getsize(text)
        _err = max(fit_size) - max(w, h)
        
        font_size += 1 if _err > 0 else -1
        font = ImageFont.truetype(font=ttf, encoding='utf-8',
                size=int(font_size))
    
    return font


def load_char_set() -> list:
    with open('charset.txt') as f:
        chars = f.read().split()

    global CHARSET_SIZE
    CHARSET_SIZE = len(chars)

    return chars


def load_font_set() -> list:
    import re
    files = os.listdir(FONT_DIR)
    fnames = []
    for root, _, files in os.walk(FONT_DIR):
        fnames.extend(os.path.join(root, f) for f in files if
                re.match(r'(.+)\.[odtfOTF]{3}', f))

    return fnames


def create_whiteboard(color='white', sample_size=(28, 28)) -> Image.Image:
    import math

    # a bit of a cheating here - charset size is 210 (15 x 14)
    bg_size = (15 * sample_size[0], 14 * sample_size[1])

    return Image.new(mode='RGBA', size=bg_size, color=color)


def create_fontboard(charset, fontset):
    from functools import reduce
    from numpy import subtract, floor_divide
    import random
    import re

    sample_size = (28, 28)
    board = create_whiteboard(sample_size=sample_size)
    init_pos = (0, 0)

    for font_file in fontset:  # FIXME - for all fonts in the fontset
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
            font = get_correct_font(
                    ttf=font_file,
                    text='H',  # for sake of performance, assume that what works
                               # for H, works for everything else
                    fit_size=(28, 28),
                    eps=8
                    )
        except OSError as e:
            print("Skipping", e.args)
            continue

        draw = ImageDraw.Draw(font_board)

        for char in charset:
            fo_x, fo_y = font.getoffset(char)
            # add a little bit of entropy
            font_offset = (
                    fo_x + random.randint(1, 3),
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

def generate_char_images(charset, size=(28, 28), *args, **kwargs):
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

    create_fontboard(charset, fontset)

    im_size = (28, 28)

