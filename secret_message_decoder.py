"""Decode a secret message from a published Google Doc grid table."""

from html.parser import HTMLParser
from urllib.request import urlopen


class _TableParser(HTMLParser):
    """Extract table rows from the simple published Google Doc format."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self._in_row = False
        self._in_cell = False
        self._current_row = []
        self._current_cell = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._in_row = True
            self._current_row = []
        elif self._in_row and tag in {"td", "th"}:
            self._in_cell = True
            self._current_cell = []

    def handle_data(self, data):
        if self._in_cell:
            self._current_cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self._in_cell:
            self._current_row.append("".join(self._current_cell).strip())
            self._current_cell = []
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = []
            self._in_row = False


def decode_secret_message(url):
    """Fetch a Google Doc URL and print the character grid it describes."""
    with urlopen(url) as response:
        html = response.read().decode("utf-8")

    parser = _TableParser()
    parser.feed(html)

    grid = {}
    for row in parser.rows[1:]:
        if len(row) < 3:
            continue

        x = int(row[0])
        char = row[1]
        y = int(row[2])
        grid[(x, y)] = char

    if not grid:
        return

    max_x = max(x for x, _ in grid)
    max_y = max(y for _, y in grid)

    for y in range(max_y + 1):
        print("".join(grid.get((x, y), " ") for x in range(max_x + 1)))


if __name__ == "__main__":
    decode_secret_message(
        "https://docs.google.com/document/d/e/"
        "2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub"
    )
