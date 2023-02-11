import sqlite3
import sys
from absl import app
from absl import flags
from colored import fg, bg, attr

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
Information to search about the card.

Filter Prefixes:
  - n: Filter by card name.
    e.g "n:Max" will get cards that have "Max" in the name.
  - d: Filter by card description.
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


def main(argv):
    query = FLAGS.query
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

    for i in range(len(query_parts)):
        f = query_parts[i]
        assert len(f) == 2
        sql_query += '{} LIKE "%{}%"'.format(f[0], f[1])
        if i < len(query_parts) - 1:
            sql_query += " AND "

    con = sqlite3.connect("sql.db")
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
    for res in cur.execute(sql_query):
        print(
            f"""
{color("Name: ", "blue")} {res[columns["CardName"]]}
{color("Type(s): ", "blue")} {res[columns["Types"]]}
{color("Desc: ", "blue")} {res[columns["Description"]]}
        """
        )
        break

    # d = res.fetchall()
    # print(d)


if __name__ == "__main__":
    app.run(main)
