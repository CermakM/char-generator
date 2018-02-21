"""Generate character images for different fonts and stores them"""

import os
import re
import sys

from . import utils
from PIL import Image, ImageFont, ImageDraw


class CharImageGenerator:
    """Character image generator class.
    Given character set and font file, can generate character images and create Keras-like
    directory structure.
    """
    default_out_dir = 'dataset'

    def __init__(self, out_dir: str = None, font_dct: dict = None, charset: list = None):
        """Initialize class."""
        self.out_dir = out_dir or self.default_out_dir
        self.font_dct = font_dct
        self.charset = charset

        self.charset_size = 0 if charset is None else len(charset)

    @classmethod
    def load(cls, charset_path, fonts_path, out_dir=None):
        """Loads characters and fonts and initializes CharImageGenerator class."""

        charset = cls.load_char_set(path=charset_path)
        font_dct = cls.load_font_set(path=fonts_path)

        return cls(out_dir=out_dir, font_dct=font_dct, charset=charset)

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

    def create_charset_dir(self, charset: list = None, dir_name='charset', test_train_split=True, create_parent_dir=False):
        """Create charset directory with structure matching Keras directory model.
        If custom charset provided, prefers this one, otherwise uses the one provided when initializing the generator.
        """

        dir_path = os.path.join(self.out_dir, dir_name)

        if charset is None:
            charset = self.charset

        if not os.path.isdir(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=create_parent_dir)
            except (FileExistsError, FileNotFoundError) as e:
                print("Directory {dir} passed as `prefix` does not exist."
                      " Use `create_parent_dir=True` to create prefix directory.".format(dir=dir_path),
                      file=sys.stderr)
                raise e

        for char in charset:
            char_ascii = ord(char)
            char_dir = "{charset_dir}/{char_dir}".format(charset_dir=dir_path, char_dir=char_ascii)
            try:
                os.mkdir(char_dir)
            except FileExistsError:
                # Directory has already been created
                continue

        return dir_path

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
                self.font_dct[font_name] = ImageFont.truetype(font=font.path, size=font_size)
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

    def generate_char_images(self, sample_size=(32, 32), bgcolor='#f6f6f6', fontcolor='black'):
        """Generate character images for each character in the charset using given font."""
        # TODO
        pass

    def create_and_save_charsets(self, sample_size=(32, 32), bgcolor='#f6f6f6', fontcolor='black'):
        """Create char images from charset for each font in fontset and saves it into predefined directory structure."""
        charset_dir = self.create_charset_dir(charset=self.charset, create_parent_dir=True)

        for font_name, font in self.font_dct.items():
            for char in self.charset:
                try:
                    char_img = self.create_char_image(char, font_name, sample_size, bgcolor, fontcolor)
                except OSError:
                    # Skip the font completely
                    break
                # Create augmanted images

                char_img_path = "{charset_dir}/{char_dir}/{font_name}.png".format(
                    charset_dir=charset_dir,
                    char_dir=ord(char),  # The directory structure expects char ordinal
                    font_name=font_name
                )
                char_img.save(fp=char_img_path, formet='png')

    def create_sprites(self, sample_size=(32, 32)):
        """Create sprites for each font provided in fontset and saves it as .png into IMG_DIR.
        Characters given by charset are drawn on a spritesheet.
        """

        if not self.font_dct or not self.charset:
            print("`fontset` has not been initialized", file=sys.stderr)
            return

        n_samples = utils.get_near_dim_2d(len(self.charset))
        board = utils.create_whiteboard(n_samples=n_samples, sample_size=sample_size)

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
            try:
                font.size = utils.estimate_font_size(
                    font=font,
                    text='H',  # for sake of performance, assume that what works
                    # for H, works for everything else
                    fit_size=(32, 32),
                    eps=max(sample_size) // 10
                )
            except OSError as e:
                print("Skipping", font_name, e.args)

            draw = ImageDraw.Draw(font_board)

            init_pos = (0, 0)
            for char in self.charset:
                # position of char in the sample
                char_loc = utils.get_text_loc_in_sample(text=char, font=font, sample_size=sample_size)

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
