"""Data augmentation module."""

import argparse
import os
import sys
import random

import numpy as np

from scipy import ndarray

# image processing library
from skimage import transform
from skimage import util
from skimage import io


def random_rotation(image_array: ndarray):
    """Pick a random degree of rotation between 25% on the left and 25% on the right."""
    random_degree = random.uniform(-25, 25)
    return transform.rotate(image_array, random_degree, mode='symmetric')


def random_noise(image_array: ndarray):
    """Add random noise to the image."""
    return util.random_noise(image_array)


def random_translation(image_array: ndarray):
    """Apply random translation transformation to the image."""
    tform = transform.SimilarityTransform(
        translation=(random.randint(-5, 5), random.randint(-5, 5))
    )
    translated = transform.warp(image_array, tform, mode='symmetric')

    return translated


def random_warp(image_array: ndarray):
    """Apply random warp transformation to the image."""

    a = image_array.shape[1] / random.randint(4, 8)
    w = random.uniform(-1.0, 1.0) / image_array.shape[0]

    warped = image_array.copy()
    for i in range(image_array.shape[0]):
        shift = int(np.ceil(a * np.sin(2.0 * np.pi * i * w)))
        warped[i, :] = np.roll(
            warped[i, :],
            shift=shift
        )

    return warped


def apply_random_transformation(
        input_folder: str,
        output_folder: str,
        recurse=False,
        limit=None,
        ignore_label=False,
        img_type='png'):
    """Load images from directory."""
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    available_transformations = [
        random_rotation,
        random_noise,
        random_translation,
        random_warp
    ]

    # find all files paths from the input_folder
    image_files = list()
    if not recurse:
        image_files = [
            os.path.join(input_folder, f) for f in os.listdir(input_folder)
            if os.path.isfile(os.path.join(input_folder, f)) and f.endswith(img_type)
        ]
    else:
        for root, walkdir, walkfiles in os.walk(input_folder):
            image_files.extend([
                os.path.join(root, f) for f in walkfiles
                if f.endswith(img_type)
            ])

    limit = limit or len(image_files)

    num_generated_files = 0
    while num_generated_files < limit:
        # random image from the input_folder
        image_path: str = random.choice(image_files)
        # read image as an two dimensional array of pixels
        image_to_transform = io.imread(image_path, as_grey=True)
        # random num of transformation to apply

        transformation = random.choice(available_transformations)

        # apply transformation
        transformed_image = transformation(image_to_transform)

        label = ""
        if not ignore_label:
            label = image_path.rsplit('/')[-2]
        out_dir = os.path.join(output_folder, label)
        os.makedirs(out_dir, exist_ok=True)

        new_file_path = "{out_dir}/augmented_image_{id}.jpg".format(
            out_dir=out_dir,
            id=num_generated_files
        )

        # write image to the disk
        io.imsave(new_file_path, transformed_image)

        num_generated_files += 1


def parse_args(argv):
    """Parse arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-dir',
        required=True,
        help="Directory to look for images. NOTE: Does not recurse by default."
    )
    parser.add_argument(
        '-o', '--output-dir',
        default=os.path.join(os.path.dirname(__file__), 'augmented_images'),
        help="Output directory."
    )
    parser.add_argument(
        '-t', '--format',
        default='png',
        help="Image format ('png' by default)."
    )
    parser.add_argument(
        '-n', '--limit',
        default=None,
        help="Limit number of images to apply transformation to."
    )
    parser.add_argument(
        '-r', '--recurse',
        action='store_true',
        help="Recursively find images in the input directory."
    )

    return parser.parse_args(argv)


def main(argv):
    """Run."""
    args = parse_args(argv)

    apply_random_transformation(
        input_folder=args.input_dir,
        output_folder=args.output_dir,
        recurse=args.recurse,
        limit=args.limit,
        img_type=args.format
    )


if __name__ == '__main__':
    main(sys.argv[1:])
