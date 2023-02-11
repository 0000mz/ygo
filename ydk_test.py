import unittest
import ydk
import tempfile
import os


class TestFileContent:
    def __init__(self, content):
        self.file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        with self.file as f:
            f.write(content)

    @property
    def filename(self):
        return self.file.name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.unlink(self.filename)


class TestYDKImport(unittest.TestCase):
    def test_import(self):
        contents = """#main
39674352
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(1, deck.nb_cards)

    def test_import2(self):
        contents = """#main
39674352

#extra
43892408
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(2, deck.nb_cards)

    def test_import3(self):
        contents = """#main
39674352

#extra
43892408

!side
73752131
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(3, deck.nb_cards)

    def test_empty_should_fail(self):
        contents = ""
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNone(deck)

    def test_invalid_card_id_should_fail(self):
        contents = """#main
-23901
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNone(deck)

    def test_unresolved_cards_should_not_fail(self):
        contents = """#main
39674352
123909309302890

#extra
43892408

!side
73752131
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(3, deck.nb_cards)

    def test_deck_iterator(self):
        contents = """#main
39674352
73752131
43892408
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(3, deck.nb_cards)

            deck_order = set([39674352, 73752131, 43892408])
            i = 0
            for card_id in deck:
                self.assertTrue(card_id in deck_order)
                deck_order.remove(card_id)
                i += 1
            self.assertEqual(3, i)

    def test_deck_iterator2(self):
        contents = """#main
39674352

#extra
73752131
43892408
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(3, deck.nb_cards)

            deck_order = set([39674352, 73752131, 43892408])
            i = 0
            for card_id in deck:
                self.assertTrue(card_id in deck_order)
                deck_order.remove(card_id)
                i += 1
            self.assertEqual(3, i)

    def test_deck_iterator3(self):
        contents = """#main
39674352

#extra
73752131

!side
43892408
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(3, deck.nb_cards)

            deck_order = set([39674352, 73752131, 43892408])
            i = 0
            for card_id in deck:
                self.assertTrue(card_id in deck_order)
                deck_order.remove(card_id)
                i += 1
            self.assertEqual(3, i)

    def test_deck_iterator4(self):
        contents = """#main
39674352
50237654

#extra
73752131

!side
43892408
        """
        with TestFileContent(contents) as test_file:
            deck = ydk.ydk_import(test_file.filename)
            self.assertIsNotNone(deck)
            self.assertEqual(4, deck.nb_cards)

            deck_order = set([39674352, 50237654, 73752131, 43892408])
            i = 0
            for card_id in deck:
                self.assertTrue(card_id in deck_order)
                deck_order.remove(card_id)
                i += 1
            self.assertEqual(4, i)


if __name__ == "__main__":
    unittest.main()
