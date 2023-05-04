"""Main Plexorcist testing file!"""

import unittest
from plexorcist import Plexorcist


class TestPlexorcist(unittest.TestCase):
    """The main Plexorcist testing class"""

    def setUp(self):
        """Initialize Plexorcist"""

        self.plexorcist = Plexorcist()
