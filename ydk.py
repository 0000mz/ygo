import sys
import os
import sqlite3
from sql import sql_path


def is_known_card(card_id: int) -> bool:
    con = sqlite3.connect(sql_path())
    if con == None:
        return False
    cur = con.cursor()
    cur.execute(f"SELECT * FROM YuGiOhDB WHERE id={card_id}")
    res = cur.fetchone()
    return res is not None and len(res) != 0


def fetch_known_cards(cards):
    if len(cards) == 0:
        return []

    con = sqlite3.connect(sql_path())
    if con == None:
        return []
    cur = con.cursor()

    filter = " OR ".join(map(lambda card_id: f"id={card_id}", cards))
    query = f"SELECT * FROM YuGiOhDB WHERE ({filter})"
    cur.execute(query)
    res = cur.fetchall()
    if res is None:
        print("Query failure.", file=sys.stderr)
        return []
    assert type(res) == type([])
    return [el[1] for el in res]


def ydk_deck_id(name: str):
    if name == "main" or name == "extra":
        return "#" + name
    elif name == "side":
        return "!side"
    return ""


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

    def ExportToYDK(self, destination: str):
        if os.path.exists(destination):
            print("File already exists: ", destination, file=sys.stderr)
            return True

        with open(destination, "w") as f:
            for deck_name, deck_cards in self.decks.items():
                n = ydk_deck_id(deck_name)
                f.write(n + "\n")
                for card in deck_cards:
                    f.write(str(card) + "\n")
                f.write("\n")
        return True

    def FilterInvalidCards(self):
        cards = set(
            self.decks["main"] + self.decks["extra"] + self.decks["side"]
        )
        known_cards = set(fetch_known_cards(cards))
        for deck_name, deck_cards in self.decks.items():
            self.decks[deck_name] = list(
                set(deck_cards).intersection(known_cards)
            )

    # Add the card with the card_id to the deck.
    # Return true if the card is known.
    def AddCard(self, card_id: int, deck: str) -> bool:
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
                deck.AddCard(card_id, curr_deck)
            except:
                continue

    deck.FilterInvalidCards()
    if deck.nb_cards == 0:
        return None

    return deck
