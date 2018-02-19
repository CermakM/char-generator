"""Generate character images for different fonts and stores them"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont


class CharImageGenerator:
    """Character image generator class.
    Given character set and font file, can generate character images and create Keras-like
    directory structure.
    """

    def __init__(self, font_dir: str = None, data_dir: str = None, charset: list = None):
        """Initialize class."""
        self.font_dir = font_dir
        self.data_dir = data_dir
        self.charset = charset

        self.charset_size = 0 if charset is None else len(charset)
