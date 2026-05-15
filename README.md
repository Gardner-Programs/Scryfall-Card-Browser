# Scryfall Card Browser

A desktop app for searching and browsing Magic: The Gathering cards using the [Scryfall API](https://scryfall.com/docs/api), built with Kivy.

## Features

- Full-text card search using Scryfall's query syntax
- Random card discovery (with optional search filter)
- Paginated results — handles searches returning thousands of cards
- Four card image sizes: Small, Medium, Large, Ex-Large
- Click any card to expand it
- Async image loading to keep the UI responsive

## Setup

```bash
pip install -r requirements.txt
python start.py
```

## Usage

- Type any Scryfall search query into the search bar (e.g. `t:dragon cmc<=4`) and press **Search** or Enter
- Click **Random** to pull a random card matching your query (leave blank for any card)
- Use the **Size** spinner to switch image sizes — the current page re-renders automatically
- Page buttons appear below results for multi-page searches

## Search syntax

Scryfall supports a rich query language. Examples:

| Query | Finds |
|---|---|
| `t:dragon` | All dragons |
| `c:g pow>=5` | Green creatures with power 5+ |
| `set:mh3 r:mythic` | Mythic rares from Modern Horizons 3 |
| `o:"draw a card" cmc<=2` | Low-cost draw spells |

Full syntax reference: [scryfall.com/docs/syntax](https://scryfall.com/docs/syntax)
