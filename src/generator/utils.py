"""Convenient functions and classes to be used by modules"""

import random
from PIL import Image, ImageFont


def get_file_name(file):
    """Return file name without its suffix."""
    import re
    return re.search(r"([^/]+)\.(\w+)$", file).group(1)


def get_near_dim_2d(number, mode='wide') -> tuple:
    """Try to factor the number into two similiar dimensions."""
    from numpy import prod, argmin

    if number <= 2:
        return number, 1

    shape = [2, 2]
    while prod(shape) < number:
        shape[int(argmin(shape))] += 1

    return tuple(sorted(shape, reverse=(mode == 'wide')))


def estimate_font_size(font, text, fit_size, eps=3) -> int:
    """Estimate font size based on given text and fit_size.

    :returns: ImageFont object.
    """

    font_size = font.size
    w, h = font.getsize(text)
    _err = max(fit_size) - max(w, h)

    # Create pseudo-font that will be adjusted and tested against the fit_size
    _font = font
    while abs(_err) > eps:
        w, h = _font.getsize(text)
        _err = max(fit_size) - max(w, h)

        font_size += 1 if _err > 0 else -1
        _font = ImageFont.truetype(font=font.path, encoding='utf-8', size=int(font_size))

    return _font.size


def create_whiteboard(shape=None, n_samples=None, fill='#f4f4f4', sample_size=(32, 32)) -> Image.Image:
    """Computes and Creates white board (background) for the given font."""
    if not any([n_samples, shape]):
        print("Either `n_samples` or `shape` must be provided.")
        return

    if shape is None:
        assert len(n_samples) == 2, "expected `n_samples` argument to be 2-D vector, but is %i-D vector" % len(
            n_samples)
        bg_size = (n_samples[0] * sample_size[0], n_samples[1] * sample_size[1])
    else:
        assert len(shape) == 2, "expected `shape` argument to be 2-D vector, but is %i-D vector" % len(shape)
        bg_size = shape

    return Image.new(mode='RGBA', size=bg_size, color=fill)


def get_text_loc_in_sample(text, font: ImageFont, sample_size, offset='random'):
    """Calculates location of text on the given sample background."""
    from functools import reduce
    from numpy import subtract, floor_divide

    fo_x, fo_y = font.getoffset(text)
    font_offset = (fo_x, fo_y)

    if offset == 'random':
        # add a little bit of entropy
        rand_factor = min(sample_size) // 10
        font_offset = (
            fo_x + random.randint(-rand_factor, rand_factor),
            fo_y + random.randint(-rand_factor, rand_factor),
        )

    # location of char in the sample
    char_loc = reduce(subtract, (sample_size, font.getsize(text), font_offset))
    char_loc = floor_divide(char_loc, 2)

    return char_loc
