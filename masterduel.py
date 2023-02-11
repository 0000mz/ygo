import requests
from ydk import Deck
import urllib.parse
import sys


def _md_to_konami(cards):
    if len(cards) == 0:
        return []
    url = "https://www.masterduelmeta.com/api/v1/cards?_id[$in]="
    for i in range(len(cards)):
        url += cards[i].strip()
        if i < len(cards) - 1:
            url += ","
    r = requests.get(url)
    if r.status_code != 200:
        print(
            "Failed to get konami id for cards: Status Code=",
            r.status_code,
            file=sys.stderr,
        )
        return None
    if "application/json" not in r.headers["Content-Type"]:
        print("Expected json payload.", file=sys.stderr)
        return None
    payload = r.json()
    assert type(payload) == type([])
    konami_ids = [int(el["konamiID"]) for el in payload]
    return konami_ids


def masterduel_to_konami(md_cards):
    CARDS_PER_REQUEST = 32
    i = 0
    all_cards = []
    while i < len(md_cards):
        parts = md_cards[i : i + CARDS_PER_REQUEST]
        i += CARDS_PER_REQUEST
        curr_cards = _md_to_konami(parts)
        if curr_cards == None:
            print(f"Failed to get cards [{i-CARDS_PER_REQUEST}:{i}].")
            return None
        assert type(curr_cards) == type([])
        all_cards += curr_cards
    return all_cards


# Request the deck with the given name from masterduel api.
def masterduel_import(deck_name: str) -> Deck:
    url = f"https://www.masterduelmeta.com/api/v1/deck-types?name[$in]={urllib.parse.quote(deck_name)}"
    r = requests.get(url)
    if r.status_code != 200:
        print(
            f'Error getting deck "{deck_name}" from master duel',
            file=sys.stderr,
        )
        print(f"Status Code: {r.status_code}", file=sys.stderr)
        return None
    if "application/json" not in r.headers["Content-Type"]:
        print("Expected json payload from masterduel.", file=sys.stderr)
        print(f"Content type received: {r.headers['Content-Type']}")
        return None
    payload = r.json()
    if len(payload) == 0:
        print(f'No deck found with name "{deck_name}"', file=sys.stderr)
        return None

    deck_pl = payload[0]
    if (
        type(deck_pl) != type({})
        or "name" not in deck_pl
        or "deckBreakdown" not in deck_pl
    ):
        print("Information missing from deck payload.", file=sys.stderr)
        return None

    name = deck_pl["name"]
    breakdown = deck_pl["deckBreakdown"]

    deck = Deck()
    assert "cards" in breakdown

    masterduel_cards = list(set([el["card"] for el in breakdown["cards"]]))
    konami_card_ids = masterduel_to_konami(masterduel_cards)
    if konami_card_ids is None:
        print("Failed to get konami ids for deck.", file=sys.stderr)
        return None
    assert type(konami_card_ids) == type([])
    for konami_id in konami_card_ids:
        deck.AddCard(konami_id, "main")

    deck.FilterInvalidCards()
    if deck.nb_cards == 0:
        print("No cards in deck.", file=sys.stderr)
        return None
    return deck


if __name__ == "__main__":
    deck = masterduel_import("Sky Striker")
    print("Number of Cards: ", deck.nb_cards)
