"""Generate character images for different fonts and stores them"""

import os
import re
import sys

import numpy as np
import typing

from . import utils

from tensorflow import keras
from PIL import Image, ImageFont, ImageDraw

DEFAULT_OUT_DIR = 'dataset'
DEFAULT_FONT_NAME = 'default'
DEFAULT_FONT_PATH = 'fonts/default.ttf'
DEFAULT_FONT_SIZE = 20


class CharImageGenerator:
    """Character image generator class.
    Given character set and font file, can generate character images and create Keras-like
    directory structure.
    """

    def __init__(self, out_dir: str = None, font_dct: dict = None, charset: typing.Iterable = None):
        """Initialize class."""
        self.out_dir = out_dir or DEFAULT_OUT_DIR
        # Initialize default font if no fonts provided
        self.font_dct = font_dct or {
            DEFAULT_FONT_NAME: ImageFont.truetype(font=DEFAULT_FONT_PATH,
                                                  size=DEFAULT_FONT_SIZE)
        }

        if not isinstance(charset, typing.Sized) and charset is not None:
            charset = [c for c in charset]

        self.charset = charset
        self.charset_size = 0 if charset is None else len(charset)

    @classmethod
    def load(cls, charset_path, fonts_path, out_dir=None):
        """Loads characters and fonts and initializes CharImageGenerator class."""

        charset = cls.load_char_set(path=charset_path)
        font_dct = cls.load_font_set(path=fonts_path)

        return cls(out_dir=out_dir, font_dct=font_dct, charset=charset)

    def load_charset_from_array(self, charset: typing.Iterable):
        """Loads the charset into the generator."""
        assert type(charset, typing.Iterable)

        self.charset = charset

    def load_fonts_from_dct(self, font_dct: dict):
        """Loads the fontset into the generator."""
        self.font_dct = font_dct

    @staticmethod
    def load_char_set(path) -> list:
        """Load characters that are allowed from the charset.txt file."""

        with open(path) as f:
            chars = f.read().split()

        return chars

    @staticmethod
    def load_font_set(path) -> dict:
        """Walk through the default font directory and search for font files."""
        font_dct = dict()
        for root, _, files in os.walk(path):
            for file in files:
                if re.match(r'(.+)\.[odtfOTF]{3}', file):
                    font_name = utils.get_file_name(file)
                    try:
                        font_dct[font_name] = ImageFont.truetype(os.path.join(root, file))
                    except OSError:
                        print("Invalid font: '%s'" % os.path.join(root, file), file=sys.stderr)
                        continue

        return font_dct

    def create_charset_dir(self,
                           charset: list = None,
                           dir_name='charset',
                           test_train_split=True,
                           create_parent_dir=False) -> list:
        """Create charset directory with structure matching Keras directory model.
        If custom charset provided, prefers this one, otherwise uses the one provided when initializing the generator.

        :param charset: list of characters (by default picks the loaded character set)
        :param dir_name: name of the new directory (default 'charset')
        :param test_train_split: whether to create charsets for test data and train data (default True)
        :param create_parent_dir: if `out_dir` provided to the generator is non-existing directory,
        creates it (default False)
        """

        if charset is None:
            assert self.charset is not None, "`charset` argument is of type %s and " \
                                             "Char set has not been provided."
            charset = self.charset

        if test_train_split:
            dir_paths = [os.path.join(self.out_dir, s, dir_name) for s in ['test_data', 'train_data']]
        else:
            dir_paths = [os.path.join(self.out_dir, dir_name)]

        for path in dir_paths:
            if not os.path.isdir(path):
                try:
                    os.makedirs(path, exist_ok=create_parent_dir)
                except (FileExistsError, FileNotFoundError) as e:
                    print("Directory {directory} passed as `prefix` does not exist."
                          " Use `create_parent_dir=True` to create prefix directory.".format(directory=path),
                          file=sys.stderr)
                    raise e

            for char in charset:
                char_ascii = ord(char)
                char_dir = "{charset_dir}/{char_dir}".format(charset_dir=path, char_dir=char_ascii)
                try:
                    os.mkdir(char_dir)
                except FileExistsError:
                    # Directory has already been created
                    continue

        return dir_paths

    def create_char_image(self, char: chr, font_name: str, sample_size=(32, 32), bgcolor='#f6f6f6', fontcolor='black'):
        """Generate image of given size and font for each character."""

        font = self.font_dct[font_name]

        try:
            font_size = utils.estimate_font_size(
                font=font,
                text=char,  # for sake of performance, assume that what works
                # for H, works for everything else
                fit_size=(32, 32),
                eps=max(sample_size) // 10
            )
            # Sadly, setting font.size is not sufficient and it is necessary create a new font
            if font_size != font.size:
                # replace it in the dict to be estimated in the future faster
                font = ImageFont.truetype(font=font.path, size=font_size)
                self.font_dct[font_name] = font

        except OSError as e:
            print("Skipping", font_name, e.args, file=sys.stderr)
            raise OSError from e

        char_bg = Image.new(mode='RGB', color=bgcolor, size=sample_size)
        draw = ImageDraw.Draw(char_bg)

        char_loc = utils.get_text_loc_in_sample(text=char, font=font, sample_size=sample_size)
        draw.text(
            xy=char_loc,
            text=char,
            font=font,
            fill=fontcolor
        )

        return char_bg

    def generate_char_images(self, sample_size=(32, 32), bgcolor='#f6f6f6', fontcolor='black',
                             augment=False, n_samples=1, **kwargs) -> tuple:
        """Generate character images for each character in the charset using given font.

        :param augment: whether to apply random transformations to the generated images (default False)
        :param n_samples: number of samples to produce per character, every `n`th image will be augmented (default 1),
        this parameter is ignored if `augment` is False

        :returns: generator object, tuples of type (char, font_name, char_img)
        """
        image_generator = keras.preprocessing.image.ImageDataGenerator(
            rescale=1. / 255,
            shear_range=0.2,
            zoom_range=0.2,
            rotation_range=15,
            **kwargs
        )

        assert self.charset is not None, "Character set has not been provided."

        if n_samples and not augment:
            # Ignore the n_samples arguments - makes no sense to produce n same samples
            n_samples = 1

        for font_name, font in self.font_dct.items():
            for char in self.charset:
                for i in range(n_samples):
                    try:
                        char_img = self.create_char_image(char, font_name, sample_size, bgcolor, fontcolor)
                    except OSError:  # Skip the font completely
                        break

                    # if more than 1 sample is specified, the first sample will be skipped
                    if n_samples > 1 and not i:
                        yield char, font_name, char_img
                        continue

                    if augment:
                        char_img = Image.fromarray(image_generator.random_transform(np.array(char_img)))

                    yield char, font_name, char_img

    def create_and_save_charsets(self,
                                 test_train_split=True,
                                 split_ratio=0.2,
                                 sample_size=(32, 32),
                                 bgcolor='#f6f6f6',
                                 fontcolor='black',
                                 **kwargs):
        """Create char images from charset for each font in font set.
        Saves it into predefined directory structure.
        """

        assert self.charset is not None, "Character set has not been provided."

        charset_dirs = self.create_charset_dir(charset=self.charset,
                                               test_train_split=test_train_split,
                                               create_parent_dir=True)

        augment = kwargs.get('augment', True)
        n_samples = kwargs.get('n_samples', 5)

        index = 0
        mod = 1 / split_ratio
        for char, font_name, char_img in self.generate_char_images(augment=augment,
                                                                   n_samples=n_samples,
                                                                   sample_size=sample_size,
                                                                   bgcolor=bgcolor,
                                                                   fontcolor=fontcolor):

            if test_train_split:
                path = charset_dirs[index % mod != 0]
            else:
                path, = charset_dirs

            char_dir = ord(char)  # The directory structure expects char ordinal
            img_name = font_name + "_{}.png".format(index)
            img_path = os.path.join(path, str(char_dir), img_name)

            char_img.save(fp=img_path, format='png')

            index = (index + 1) % n_samples

    def create_sprites(self, sample_size=(32, 32)):
        """Create sprites for each font provided in fontset and saves it as .png into IMG_DIR.
        Characters given by charset are drawn on a spritesheet.
        """
        assert self.charset is not None, "Character set has not been provided."

        if not self.font_dct or not self.charset:
            print("`fontset` has not been initialized", file=sys.stderr)
            return

        n_samples = utils.get_near_dim_2d(len(self.charset))
        board_color = '#f4f4f4'
        board = utils.create_whiteboard(n_samples=n_samples, sample_size=sample_size, fill=board_color)

        sprites_dir = "{path}/sprites".format(path=self.out_dir)
        # Make sure sprites directory exists
        if os.path.isdir(sprites_dir) and os.listdir(sprites_dir):
            raise FileExistsError("Directory '%s' already exists and is not empty." % sys.stderr)

        os.makedirs(sprites_dir, exist_ok=True)

        for font_name, font in self.font_dct.items():
            board_name = "{path}/{ttf}-board.png".format(
                path=sprites_dir,
                ttf=font_name)
            if os.path.isfile(board_name):
                print('Skipping', board_name)
                continue

            print("Creating spritesheet", board_name, "...")
            font_board = board.copy()

            init_pos = (0, 0)
            for char in self.charset:
                try:
                    char_img = self.create_char_image(char=char, font_name=font_name,
                                                      sample_size=sample_size,
                                                      bgcolor=board_color)
                except OSError:
                    # Skip this font - probably generates raster overflow
                    break

                # position of char on the board - by default move on the x axis only
                font_board.paste(char_img, box=init_pos)

                pos = (init_pos[0] + sample_size[0], init_pos[1])
                if pos[0] % font_board.width:
                    init_pos = pos
                else:
                    # Move to the row bellow
                    init_pos = (0, init_pos[1] + sample_size[1])

            # save the board
            font_board.save(fp=board_name)
            print('Written', board_name)
