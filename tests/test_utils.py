import unittest

from src.generator import utils


class UtilsTests(unittest.TestCase):

    def test_get_near_dim(self):
        number = 210
        shape = utils.get_near_dim_2d(number, mode='wide')

        self.assertEqual(shape, (15, 14))
