from __future__ import annotations

import math

import requests
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

import asynckivy as ak


class ImageButton(ButtonBehavior, AsyncImage):
    pass


class ErrorPopup(Popup):
    error_text = StringProperty("")

    def __init__(self, error_text: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.error_text = error_text


class MainWindow(Widget):
    SIZE_REFERENCE: dict = {
        "Small":    {"name": "small",  "size": (146, 204)},
        "Medium":   {"name": "normal", "size": (300, 400)},
        "Large":    {"name": "normal", "size": (488, 680)},
        "Ex-Large": {"name": "large",  "size": (672, 936)},
    }

    card_size: str = "Medium"
    col_width: int = SIZE_REFERENCE["Medium"]["size"][0]
    page: int = 1
    page_size: int = 50
    current_search: str = ""
    current_page_cards: list = []

    # ── Rendering ────────────────────────────────────────────────

    async def display_results(self, selected_page: list) -> None:
        """Render a list of Scryfall card dicts into the results grid."""
        self.current_page_cards = selected_page
        results_grid = self.ids.results_grid
        results_grid.clear_widgets()
        size = self.SIZE_REFERENCE[self.card_size]["size"]
        img_name = self.SIZE_REFERENCE[self.card_size]["name"]
        for card in selected_page:
            await ak.sleep(0.05)
            try:
                source = card["image_uris"][img_name]
            except KeyError:
                source = card["card_faces"][0]["image_uris"][img_name]
            results_grid.add_widget(
                ImageButton(
                    source=source,
                    size_hint=(None, None),
                    size=size,
                    on_press=self.press,
                )
            )

    def size_click(self, spinner: str) -> None:
        """Re-render the current page at the newly selected card size."""
        self.card_size = spinner
        self.col_width = self.SIZE_REFERENCE[spinner]["size"][0]
        self.ids.results_grid.cols = Window.width // self.col_width
        if self.current_page_cards:
            ak.start(self.display_results(self.current_page_cards))

    def press(self, instance: ImageButton) -> None:
        """Expand a card to fill the results area on click."""
        results_grid = self.ids.results_grid
        results_grid.clear_widgets()
        results_grid.add_widget(
            ImageButton(source=instance.source, size_hint=(None, None), size=instance.size)
        )

    # ── Pagination ───────────────────────────────────────────────

    def _get_api_pages(self) -> range:
        """Return the Scryfall API page numbers needed to fill the current app page.

        Scryfall returns 175 cards per API page; the app shows page_size per view.
        """
        first = ((self.page - 1) * self.page_size) // 175 + 1
        last = ((self.page * self.page_size) - 1) // 175 + 1
        return range(first, last + 1)

    def create_page_select(self, num_results: int) -> None:
        """Build numbered page buttons below the results grid."""
        page_options = self.ids.page_options
        page_options.clear_widgets()
        max_page = math.ceil(num_results / self.page_size)
        page_options.cols = max_page
        for page in range(1, max_page + 1):
            btn = Button(text=str(page), size_hint=(None, None), size=(30, 20))
            btn.bind(on_press=self.click_page)
            page_options.add_widget(btn)

    def click_page(self, instance: Button) -> None:
        """Fetch and display the page of results corresponding to the pressed button."""
        self.page = int(instance.text)
        card_list: list = []
        api_pages = self._get_api_pages()
        for api_page in api_pages:
            response = requests.get(
                "https://api.scryfall.com/cards/search",
                {"q": self.current_search, "page": api_page},
            )
            if not response.ok:
                ErrorPopup(f"{response.reason}: could not load page {api_page}").open()
                return
            card_list.extend(response.json()["data"])
        first_api_page = min(api_pages)
        offset = ((self.page - 1) * self.page_size) - ((first_api_page - 1) * 175)
        ak.start(self.display_results(card_list[offset : offset + self.page_size]))

    # ── Search ───────────────────────────────────────────────────

    def search(self) -> None:
        """Execute a Scryfall search and display the first page of results."""
        self.current_search = self.ids.search_bar.text.strip()
        if not self.current_search:
            ErrorPopup("Search cannot be blank.").open()
            return

        response = requests.get(
            "https://api.scryfall.com/cards/search", {"q": self.current_search}
        )
        if not response.ok:
            data = response.json()
            ErrorPopup(f"{response.reason}:\n{data.get('warnings', data.get('details', ''))}").open()
            return

        cards = response.json()
        card_list: list = cards["data"]
        self.page = 1
        ak.start(self.display_results(card_list[: self.page_size]))
        self.create_page_select(cards["total_cards"])

    def random_search(self) -> None:
        """Fetch a single random card matching the current search text."""
        query = self.ids.search_bar.text.strip()
        params = {"q": query} if query else {}
        response = requests.get("https://api.scryfall.com/cards/random", params)
        if not response.ok:
            data = response.json()
            ErrorPopup(f"{response.reason}:\n{data.get('warnings', data.get('details', ''))}").open()
            return

        card = response.json()
        img_name = self.SIZE_REFERENCE[self.card_size]["name"]
        size = self.SIZE_REFERENCE[self.card_size]["size"]
        try:
            source = card["image_uris"][img_name]
        except KeyError:
            source = card["card_faces"][0]["image_uris"][img_name]

        results_grid = self.ids.results_grid
        results_grid.clear_widgets()
        results_grid.add_widget(
            ImageButton(source=source, size_hint=(None, None), size=size, on_press=self.press)
        )


class ScryApp(App):
    def build(self) -> MainWindow:
        return MainWindow()


if __name__ == "__main__":
    ScryApp().run()
