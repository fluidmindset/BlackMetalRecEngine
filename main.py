"""Small client for searching the Encyclopaedia Metallum (Metal Archives)."""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ARCHIVE_URL = "https://www.metal-archives.com/search"


class _LinkParser(HTMLParser):
	def __init__(self) -> None:
		super().__init__()
		self.links: list[tuple[str, str]] = []
		self._href: str | None = None
		self._text: list[str] = []

	def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
		if tag == "a":
			self._href = dict(attrs).get("href")
			self._text = []

	def handle_data(self, data: str) -> None:
		if self._href is not None:
			self._text.append(data)

	def handle_endtag(self, tag: str) -> None:
		if tag == "a" and self._href:
			text = " ".join("".join(self._text).split())
			if text:
				self.links.append((text, self._href))
			self._href = None


def search_bands(query: str, *, timeout: int = 15) -> list[dict[str, str]]:
	"""Search the black-metal band archive and return matching band links."""
	if not query.strip():
		raise ValueError("query must not be empty")

	params = urlencode({"searchString": query, "band_genre": "Black Metal"})
	request = Request(
		f"{ARCHIVE_URL}/band/?{params}",
		headers={"User-Agent": "BlackMetalRecEngine/1.0"},
	)
	with urlopen(request, timeout=timeout) as response:
		parser = _LinkParser()
		parser.feed(response.read().decode("utf-8", errors="replace"))

	return [
		{"name": name, "url": url}
		for name, url in parser.links
		if "/band/" in url
	]


if __name__ == "__main__":
	import argparse

	cli = argparse.ArgumentParser(description="Search the black-metal band archive")
	cli.add_argument("query")
	args = cli.parse_args()
	for band in search_bands(args.query):
		print(f"{band['name']}: {band['url']}")
