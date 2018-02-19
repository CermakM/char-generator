"""Runs generator to create character image dataset.

This script assumes that the fonts have already been obtained using scraper.
"""

import argparse

from src.generator import CharImageGenerator


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--charset',
        help="Path to a file containing characters to be turned into images, separated by newlines."
    )

    parser.add_argument(
        '--font-dir',
        help="Path to a directory containing font files (obtained by scraper), separated by newlines."
    )

    parser.add_argument(
        '-p', '--prefix',
        default='./',
        help="If provided, generated directory will be prefixed with the value of `prefix`."
    )

    args = parser.parse_args()

    gen = CharImageGenerator.load(charset_path=args.charset,
                                  fontset_path=args.font_dir,
                                  create_charset_dir=True,
                                  prefix=args.prefix
                                  )

    gen.create_sprites()
    gen.create_and_save_charsets()


if __name__ == '__main__':
    # TODO: this script could be more modular - could accept charset and fonts directory as a parameter
    main()
