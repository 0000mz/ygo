# ygo

Tool for querying yugioh cards.

## Getting Started [Linux]
1. Clone the repository: `git clone https://github.com/bee-mo/ygo.git`.
2. Run `sh ./install.sh`.
3. Run `./ygo --help`.

## Importing A Deck
### Importing from YDK
You can import a deck from a `ydk` file:
`ygo --import_deck "<filaname>" --deck_name "<name of deck>"`.

This will import and save that deck for future queries. That way you can query cards from only that deck.

### Importing from MasterDuel Meta
You can import a deck straight from [**MasterDuel Meta**](https://www.masterduelmeta.com/): `ygo --import_mdm "HEROs"`. This will import and save the **HEROs** deck from for you to query against.

NOTE: The MasterDuel Meta deck name is case sensitive, so you must make sure it's the exact casing. Otherwise, it will fail to find the deck.

## Querying
- Query the card name: `ygo --query n:sky`.
- Query the card description: `ygo --query d:trap`.
- Query name and description: `ygo --query "n:sky d:trap"`.
- Pinning a query to a deck: `ygo --query "n: sky d:trap" --use_deck="Sky Striker"`