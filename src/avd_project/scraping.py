from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from avd_project.config import BOOKS_BASE_URL, RAW_DATA_DIR


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


@dataclass(frozen=True)
class Book:
    title: str
    price_gbp: Decimal
    rating: int
    availability: str
    category: str
    product_url: str
    image_url: str


def fetch_html(url: str, timeout: int = 20) -> BeautifulSoup:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_category_urls(base_url: str = BOOKS_BASE_URL) -> list[tuple[str, str]]:
    soup = fetch_html(base_url)
    category_links = soup.select(".side_categories ul.nav-list ul li a")

    categories = []
    for link in category_links:
        category_name = link.get_text(strip=True)
        category_url = urljoin(base_url, link["href"])
        categories.append((category_name, category_url))

    return categories


def parse_price(price_text: str) -> Decimal:
    clean_price = price_text.replace("£", "").strip()
    return Decimal(clean_price)


def parse_rating(article: BeautifulSoup) -> int:
    rating_class = article.select_one("p.star-rating")["class"]
    rating_name = next(item for item in rating_class if item in RATING_MAP)
    return RATING_MAP[rating_name]


def parse_book_card(article: BeautifulSoup, category: str, page_url: str) -> Book:
    title_node = article.select_one("h3 a")
    price_node = article.select_one(".price_color")
    availability_node = article.select_one(".availability")
    image_node = article.select_one(".image_container img")

    product_url = urljoin(page_url, title_node["href"])
    image_url = urljoin(page_url, image_node["src"])

    return Book(
        title=title_node["title"],
        price_gbp=parse_price(price_node.get_text(strip=True)),
        rating=parse_rating(article),
        availability=availability_node.get_text(" ", strip=True),
        category=category,
        product_url=product_url,
        image_url=image_url,
    )


def get_next_page_url(soup: BeautifulSoup, page_url: str) -> str | None:
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None
    return urljoin(page_url, next_link["href"])


def scrape_category(category: str, category_url: str, delay_seconds: float = 0.2) -> list[Book]:
    books: list[Book] = []
    page_url: str | None = category_url

    while page_url:
        soup = fetch_html(page_url)
        cards = soup.select("article.product_pod")
        books.extend(parse_book_card(card, category, page_url) for card in cards)
        page_url = get_next_page_url(soup, page_url)

        if page_url:
            sleep(delay_seconds)

    return books


def scrape_books(base_url: str = BOOKS_BASE_URL) -> pd.DataFrame:
    all_books: list[Book] = []

    for category, category_url in get_category_urls(base_url):
        all_books.extend(scrape_category(category, category_url))

    return pd.DataFrame([asdict(book) for book in all_books])


def scrape_books_to_csv(output_path: str | Path | None = None) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = Path(output_path) if output_path else RAW_DATA_DIR / "books_raw.csv"

    df = scrape_books()
    df.to_csv(destination, index=False, encoding="utf-8")
    return destination
