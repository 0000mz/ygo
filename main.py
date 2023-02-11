import re
import sqlite3
import sys
import os
from absl import app
from absl import flags
from colored import fg, bg, attr
from appdata import AppDataPaths
import ydk
import shutil
import toml

# TODO: Allow saving deck and filtering by deck.
# TODO: Add color highlighting of the specific word that the user queried for.

"""
ygo: Search Yu-Gi-Ho Card Database
"""

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "query",
    "",
    """
Information to search about the card. Use --use_deck to search only
cards from that deck.

Filter Prefixes:
  - n: Filter by card name.
  - d: Filter by card description.
  Example Queries: 
    --query=n:dark         # Search all cards with dark in the name.
    --query=d:graveyard    # Search all cards with graveyard in the description.
""",
)
flags.DEFINE_string("use_deck", "", "A deck to pin a query to.")

flags.DEFINE_boolean("list_decks", False, "List all saved decks.")

flags.DEFINE_string(
    "import_deck", "", "Import a deck from supported formats: ydk"
)
flags.DEFINE_string(
    "deck_name",
    "",
    """Use in conjunction with --import_deck. Specify the name to save
  the deck as.
  """,
)

# Return the first word in the string
def current_word(value: str) -> str:
    parts = value.split(" ")
    if len(parts) == 0:
        return None
    return parts[0]


def strip_leading_quotes(value: str) -> str:
    if len(value) < 2:
        return None
    return value[1 : len(value) - 1]


def current_quoted_string(value: str) -> str:
    if len(value) < 2:
        return None

    def is_quote(val):
        return val == '"' or val == "'"

    stack = [value[0]]
    i = 1
    while len(stack) != 0 and i < len(value):
        c = value[i]
        if is_quote(c):
            # If the quote matches, pop from stack.
            if stack[0] == c:
                stack = stack[1:]
            # Else, add to stack.
            else:
                stack = [] + stack
        i += 1
    return None if len(stack) > 0 else strip_leading_quotes(value[:i])


def get_filter_value(prefix: str, filter: str) -> str:
    if prefix not in filter:
        return None

    pos = filter.index(prefix)
    if pos > 0 and filter[pos - 1] != " ":
        return None

    start_i = pos + len(prefix)
    if start_i < len(filter) and (
        filter[start_i] == '"' or filter[start_i] == "'"
    ):
        return current_quoted_string(filter[start_i:])
    else:
        return current_word(filter[start_i:])


def color(msg: str, color: str) -> str:
    return f"{fg(color)}{msg}{attr('reset')}"


# Get the filter information based on the filter string.
def get_filter_params(filter: str):
    filter_params = {
        "name": get_filter_value("n:", filter),
        "desc": get_filter_value("d:", filter),
    }
    return filter_params


# Get all cards from a deck
def get_deck_cards(deck_name):
    if len(deck_name) == 0:
        return None
    cfg = load_app_cfg()
    if "decks" not in cfg or len(cfg["decks"]) == 0:
        return None
    if deck_name not in cfg["decks"]:
        return None

    deck_path = cfg["decks"][deck_name]
    assert os.path.exists(deck_path)
    deck = ydk.ydk_import(deck_path, False)
    assert deck is not None
    return deck


def highlight_instances(msg: str, value: str, clr: str) -> str:
    if value is None:
        return msg
    curr_i = 0

    res = ""
    while True:
        next_pos = re.search(value, msg[curr_i:], re.IGNORECASE)
        if next_pos == None:
            break
        prev_i = curr_i
        curr_i += next_pos.end()
        res += msg[prev_i : prev_i + next_pos.start()]  # Add non-matching word
        res += color(
            msg[prev_i + next_pos.start() : prev_i + next_pos.end()], clr
        )

    res += msg[curr_i:]
    return res


def query_cards(query, deck_name):

    if query is None or len(query) == 0:
        print("No queries.", file=sys.stderr)
        sys.exit(1)

    p = get_filter_params(query)

    query_parts = []
    if p["name"] is not None:
        query_parts.append(["CardName", p["name"]])
    if p["desc"] is not None:
        query_parts.append(["Description", p["desc"]])

    if len(query_parts) == 0:
        print("No query parameters.", file=sys.stderr)
        sys.exit(1)

    dbname = "YuGiOhDB"
    sql_query = "SELECT * from {} where ".format(dbname)

    deck_cards = get_deck_cards(deck_name)
    if deck_cards is not None:
        deck_subfilter_query = ""
        i = 0
        for card_id in deck_cards:
            deck_subfilter_query += f"id={card_id} "
            if i < deck_cards.nb_cards - 1:
                deck_subfilter_query += "OR "
            i += 1
        if i > 0:
            sql_query += f"({deck_subfilter_query}) AND "

    for i in range(len(query_parts)):
        f = query_parts[i]
        assert len(f) == 2
        a = f[0]
        b = f[1]
        sql_query += f'({a} LIKE "%{b}%")'
        if i < len(query_parts) - 1:
            sql_query += " AND "

    with sqlite3.connect("sql.db") as con:
        cur = con.cursor()
        columns = {
            "CardName": 0,
            "id": 1,
            "CardType": 2,
            "Attribute": 3,
            "Property": 4,
            "Types": 5,
            "Level": 6,
            "ATK": 7,
            "DEF": 8,
            "Link": 9,
            "PendulumScale": 10,
            "Description": 11,
        }

        # print("Query: ", sql_query)
        for res in cur.execute(sql_query.strip()):
            print(
                f"""
  {color("Name: ", "blue")} {highlight_instances(res[columns["CardName"]], p["name"], "red")}
  {color("Type(s): ", "blue")} {res[columns["Types"]]}
  {color("Desc: ", "blue")} {highlight_instances(res[columns["Description"]], p["desc"], "red")}
          """
            )


def list_decks():
    app = AppDataPaths("ygo")
    if not os.path.exists(app.app_data_path):
        print(
            "No saved decks. Use --import_deck to import ydk deck.",
            file=sys.stderr,
        )
        sys.exit(1)
    cfg = load_app_cfg()
    if "decks" not in cfg or len(cfg["decks"]) == 0:
        print("No decks saved. Use --import_deck to import a ydk deck.")
        sys.exit(1)
    print("Decks:")
    for deck_name, _ in cfg["decks"].items():
        print("  - ", deck_name)


def cfg_file_location():
    app = AppDataPaths("ygo")
    return os.path.join(app.app_data_path, "config.toml")


# Load the application configutation.
def load_app_cfg():
    try:
        cfgloc = cfg_file_location()
        if not os.path.exists(cfgloc):
            return {}
        with open(cfgloc, "r") as f:
            return toml.load(f)
    except Exception as e:
        print(e)
        sys.exit(1)


def save_app_cfg(cfg):
    assert cfg is not None
    try:
        cfgloc = cfg_file_location()
        print("Saving config to: ", cfgloc)
        with open(cfgloc, "w") as f:
            toml.dump(cfg, f)
            return True
    except Exception as e:
        print("Error saving app config.", file=sys.stderr)
        print(e)
    return False


def import_deck(deck_file: str, deck_name: str):
    if not os.path.exists(deck_file):
        print("File not found: ", deck_file, file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(deck_file):
        print("Deck file is not a file: ", deck_file, file=sys.stderr)
        sys.exit(1)
    if len(deck_name) == 0:
        print(
            "No deck name provided. Use --deck_name to specify the name of the deck.",
            file=sys.stderr,
        )
        sys.exit(1)
    deck = ydk.ydk_import(deck_file)
    if deck is None:
        print("Deck import failed.", file=sys.stderr)

    print(f"Number of unique cards in deck: {deck.nb_cards}")
    app = AppDataPaths("ygo")
    if not os.path.exists(app.app_data_path):
        os.mkdir(app.app_data_path)
    assert os.path.isdir(app.app_data_path)

    dst = os.path.join(app.app_data_path, "{}.ydk".format(deck_name))
    i = 1
    while os.path.exists(dst):
        dst = os.path.join(app.app_data_path, "{}_{}.ydk".format(deck_name, i))
        i += 1
    shutil.copy(deck_file, dst)

    cfg = load_app_cfg()
    assert cfg is not None
    if "decks" not in cfg:
        cfg["decks"] = {}

    cfg["decks"][deck_name] = dst
    assert save_app_cfg(cfg)


def main(argv):
    if len(FLAGS.query) > 0:
        return query_cards(FLAGS.query, FLAGS.use_deck)
    elif FLAGS.list_decks:
        return list_decks()
    elif len(FLAGS.import_deck) > 0:
        return import_deck(FLAGS.import_deck, FLAGS.deck_name)


if __name__ == "__main__":
    app.run(main)
