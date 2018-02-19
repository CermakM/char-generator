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

    def test_create_charset_dir_correct_path(self):
        """Check if the path to the new directory has been returned."""
        prefix = tempfile.mkdtemp()
        gen = CharImageGenerator(out_dir=prefix)
        charset_dir = gen.create_charset_dir(self.TEST_CHARSET, create_parent_dir=True)

        self.assertTrue(charset_dir.startswith(prefix))

    def test_create_charset_dir(self):
        """Check if the new directory contains subdirectories matching the test_charset."""
        prefix = tempfile.mkdtemp()
        gen = CharImageGenerator(out_dir=prefix)
        charset_dir = gen.create_charset_dir(self.TEST_CHARSET, create_parent_dir=True)
        charset_ascii = set(ord(c) for c in self.TEST_CHARSET)
        subdirs = set(int(dir_name) for dir_name in os.listdir(charset_dir))

        self.assertEqual(subdirs, charset_ascii)
