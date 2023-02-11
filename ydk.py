import sys
import os
import sqlite3


def is_known_card(card_id: int) -> bool:
    # return True
    con = sqlite3.connect("sql.db")
    if con == None:
        return False
    cur = con.cursor()
    cur.execute(f"SELECT * FROM YuGiOhDB WHERE id={card_id}")
    return len(cur.fetchone()) != 0


class Deck:
    def __init__(self):
        self.decks = {"main": [], "extra": [], "side": []}

    def __iter__(self):
        self.cur = 0
        return self

    def __next__(self):
        deck_ords = ["main", "side", "extra"]
        curr_deck = -1
        deck_found = False
        card_index = None

        prev_s = 0
        s = 0
        for d in deck_ords:
            curr_deck += 1
            assert d in self.decks
            prev_s = s
            s += len(self.decks[d])
            if s > self.cur:
                deck_found = True
                card_index = self.cur - prev_s
                break

        self.cur += 1
        if not deck_found:
            raise StopIteration
        return self.decks[deck_ords[curr_deck]][card_index]

    # Add the card with the card_id to the deck.
    # Return true if the card is known.
    def AddCard(self, card_id: int, deck: str, verify) -> bool:
        if verify and not is_known_card(card_id):
            return False
        assert deck in self.decks
        if card_id not in self.decks[deck]:
            self.decks[deck].append(card_id)
        return True

    @property
    def nb_cards(self):
        ct = 0
        for k, v in self.decks.items():
            ct += len(v)
        return ct


# Import a deck from a YDK file.
def ydk_import(fname: str, verify=True) -> Deck:
    if not os.path.exists(fname) or not os.path.isfile(fname):
        print("File does not exist: ", fname, file=sys.stderr)
        return None

    deck = Deck()
    curr_deck = None

    nb_cards = 0
    unresolved_cards = set()
    with open(fname, "r") as f:
        for line in f:
            token = line.strip()
            if token == "#main":
                curr_deck = "main"
            elif token == "#extra":
                curr_deck = "main"
            elif token == "!side":
                curr_deck = "side"

            if len(token) == 0 or curr_deck == None:
                continue
            try:
                card_id = int(token)
                if not deck.AddCard(card_id, curr_deck, verify):
                    unresolved_cards.Add(card_id)
                else:
                    nb_cards += 1
            except:
                continue

    if nb_cards == 0:
        return None

    if len(unresolved_cards) > 0:
        print("Unresolved card ids:")
        for card in unresolved_cards:
            print("\t", card)
        return None
    return deck
