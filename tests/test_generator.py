import os
import tempfile
import unittest

from src.generator import CharImageGenerator


class GeneratorTests(unittest.TestCase):
    """Class containing tests for character generator."""
    TEST_CHARSET = ['A', 'a', '0', '.', '&', '^']

    def test_char_img_gen_init(self):
        char_gen = CharImageGenerator()

        self.assertIsNotNone(char_gen)

    def test_load_charset(self):
        fd, f_path = tempfile.mkstemp()
        for char in self.TEST_CHARSET:
            os.write(fd, "{}\n".format(char).encode())
        os.close(fd)
        loaded_charset = CharImageGenerator.load_char_set(f_path)

        self.assertSequenceEqual(self.TEST_CHARSET, loaded_charset)

    def test_create_charset_dir_correct_path_nosplit(self):
        """Check if the path to the new directory has been returned."""
        prefix = tempfile.mkdtemp()
        gen = CharImageGenerator(out_dir=prefix)
        charset_dir, = gen.create_charset_dir(self.TEST_CHARSET, test_train_split=False, create_parent_dir=True)

        self.assertTrue(charset_dir.startswith(prefix))

    def test_create_charset_dir_nosplit(self):
        """Check if the new directory contains subdirectories matching the test_charset."""
        prefix = tempfile.mkdtemp()
        gen = CharImageGenerator(out_dir=prefix)
        charset_dir, = gen.create_charset_dir(self.TEST_CHARSET, test_train_split=False, create_parent_dir=True)
        charset_ascii = set(ord(c) for c in self.TEST_CHARSET)
        subdirs = set(int(dir_name) for dir_name in os.listdir(charset_dir))

        self.assertEqual(subdirs, charset_ascii)

    def test_create_charset_dir_split(self):
        """Check if the new directory contains subdirectories matching the test_charset."""
        prefix = tempfile.mkdtemp()
        gen = CharImageGenerator(out_dir=prefix)
        charset_dirs = gen.create_charset_dir(self.TEST_CHARSET, test_train_split=True, create_parent_dir=True)
        charset_ascii = set(ord(c) for c in self.TEST_CHARSET)

        for ch_dir in charset_dirs:
            subdir = set(int(dir_name) for dir_name in os.listdir(ch_dir))
            self.assertEqual(subdir, charset_ascii)

    def test_generate_char_images(self):
        import types
        prefix = tempfile.mkdtemp()
        n_samples = 3
        gen = CharImageGenerator(out_dir=prefix, charset=self.TEST_CHARSET)
        image_generator = gen.generate_char_images(n_samples=n_samples, augment=True)

        self.assertIsInstance(image_generator, types.GeneratorType)

        expected_img_count = len(self.TEST_CHARSET) * n_samples
        img_count = sum(1 for _ in image_generator)

        self.assertEqual(img_count, expected_img_count, msg="Number of generated images"
                                                            " does not match the expected value.")

    def test_create_and_save_charsets_default(self):
        prefix = tempfile.mkdtemp()
        n_samples = 3
        gen = CharImageGenerator(out_dir=prefix, charset=self.TEST_CHARSET)
        gen.create_and_save_charsets(test_train_split=True, n_samples=n_samples, augment=True)

        # check that the dataset has been split into the test and train directory
        self.assertEqual(set(os.listdir(prefix)), {'test_data', 'train_data'})
        #   and that they are not empty
        expected_img_count = len(self.TEST_CHARSET) * n_samples
        img_count = 0
        for root, _, walkfiles in os.walk(prefix):
            img_count += len(walkfiles)

        self.assertEqual(img_count, expected_img_count, msg="Number of created images"
                                                            " does not match the expected value.")
