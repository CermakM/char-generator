import os
import tempfile
import unittest

from numpy import array_equal
from skimage import io

from src.generator import data_augmentation as daug


TEST_DATA_ONES = os.path.abspath('test_data/49')
TEST_DATA_THREES = os.path.abspath('test_data/51')


class TestDataAugmentation(unittest.TestCase):
    """Tests for data_augmentation module."""

    def test_random_rotation(self):
        """Test random rotation."""
        images = [
            io.imread(os.path.join(TEST_DATA_ONES, fp), as_grey=True)
            for fp in os.listdir(TEST_DATA_ONES)
        ]
        img = images[0]
        transformed_img = daug.random_rotation(img)

        self.assertTrue(transformed_img.any())
        self.assertFalse(array_equal(img, transformed_img))

    def test_random_noise(self):
        """Test random noise."""
        images = [
            io.imread(os.path.join(TEST_DATA_ONES, fp), as_grey=True)
            for fp in os.listdir(TEST_DATA_ONES)
        ]
        img = images[0]
        transformed_img = daug.random_noise(img)

        self.assertTrue(transformed_img.any())
        self.assertFalse(array_equal(img, transformed_img))

    def test_random_translation(self):
        """Test random translation."""
        images = [
            io.imread(os.path.join(TEST_DATA_ONES, fp), as_grey=True)
            for fp in os.listdir(TEST_DATA_ONES)
        ]
        img = images[0]
        transformed_img = daug.random_warp(img)

        self.assertTrue(transformed_img.any())
        self.assertFalse(array_equal(img, transformed_img))

    def test_random_warp(self):
        """Test random warp."""
        images = [
            io.imread(os.path.join(TEST_DATA_ONES, fp), as_grey=True)
            for fp in os.listdir(TEST_DATA_ONES)
        ]
        img = images[0]
        transformed_img = daug.random_warp(img)

        import matplotlib.pyplot as plt
        io.imshow(transformed_img)
        plt.show()

        self.assertTrue(transformed_img.any())
        self.assertFalse(array_equal(img, transformed_img))

    def test_apply_random_transform(self):
        """Test random transformation."""
        output_folder = tempfile.mkdtemp(prefix='test_', suffix='_augment')
        limit = 5
        daug.apply_random_transformation(
            input_folder=TEST_DATA_ONES,
            output_folder=output_folder,
            limit=limit
        )

        self.assertEqual(len(os.listdir(output_folder)), limit)
