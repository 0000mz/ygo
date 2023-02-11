import unittest
import ydk
import tempfile
import os


class TestYDKImport(unittest.TestCase):
    def test_query(self):
        cards = [7459013, 36099130, 4367330]
        known_cards = ydk.fetch_known_cards(cards)
        self.assertEqual(len(cards), len(known_cards))

    def test_query2(self):
        cards = [7459013, 36099130, 4367330, 1920391203201193]
        known_cards = ydk.fetch_known_cards(cards)
        self.assertEqual(len(cards) - 1, len(known_cards))


if __name__ == "__main__":
    unittest.main()
