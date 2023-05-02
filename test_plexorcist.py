"""Main Plexorcist testing file!"""

import unittest
from plexorcist import Plexorcist


class TestPlexorcist(unittest.TestCase):
    """The main Plexorcist testing class

    Args:
        unittest (_type_): _description_
    """

    def setUp(self):
        """Initialize Plexorcist"""

        self.plexorcist = Plexorcist()
