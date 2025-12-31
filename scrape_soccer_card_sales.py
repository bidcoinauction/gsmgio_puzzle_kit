#!/usr/bin/env python3
"""Scrape finalized (sold) soccer card listings from eBay.

Example:
  python scrape_soccer_card_sales.py --query "messi rookie" --pages 3 --output messi_sales.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

EBAY_SEARCH_URL = "https://www.ebay.com/sch/i.html"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

PRICE_RE = re.compile(r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)")


@dataclass
class Listing:
    title: str
    price: Optional[Decimal]
    shipping: Optional[Decimal]
    total: Optional[Decimal]
    sold_date: str
    url: str


def parse_money(value: str) -> Optional[Decimal]:
    match = PRICE_RE.search(value.replace("$", ""))
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", ""))
    except InvalidOperation:
        return None


def extract_listings(html: str) -> Iterable[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.select("li.s-item"):
        title_el = item.select_one("h3.s-item__title")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if title == "Shop on eBay":
            continue

        price_el = item.select_one("span.s-item__price")
        price_text = price_el.get_text(strip=True) if price_el else ""
        price = parse_money(price_text)

        shipping_el = item.select_one("span.s-item__shipping")
        shipping_text = shipping_el.get_text(strip=True) if shipping_el else ""
        shipping = parse_money(shipping_text)

        total = None
        if price is not None:
            total = price + (shipping or Decimal("0"))

        sold_date_el = item.select_one("span.s-item__ended-date")
        sold_date = sold_date_el.get_text(strip=True) if sold_date_el else ""

        link_el = item.select_one("a.s-item__link")
        url = link_el["href"] if link_el and link_el.has_attr("href") else ""

        yield Listing(
            title=title,
            price=price,
            shipping=shipping,
            total=total,
            sold_date=sold_date,
            url=url,
        )


def build_search_url(query: str, page: int) -> str:
    params = {
        "_nkw": query,
        "LH_Sold": "1",
        "LH_Complete": "1",
        "_pgn": str(page),
    }
    return f"{EBAY_SEARCH_URL}?{urlencode(params)}"


def fetch_page(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def scrape_listings(query: str, pages: int, delay: float) -> list[Listing]:
    listings: list[Listing] = []
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        for page in range(1, pages + 1):
            url = build_search_url(query, page)
            html = fetch_page(session, url)
            page_listings = list(extract_listings(html))
            listings.extend(page_listings)
            if delay and page < pages:
                time.sleep(delay)
    return listings


def write_csv(listings: Iterable[Listing], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "title",
            "price",
            "shipping",
            "total",
            "sold_date",
            "url",
        ])
        for listing in listings:
            writer.writerow([
                listing.title,
                f"{listing.price}" if listing.price is not None else "",
                f"{listing.shipping}" if listing.shipping is not None else "",
                f"{listing.total}" if listing.total is not None else "",
                listing.sold_date,
                listing.url,
            ])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape finalized sale prices for soccer sports cards from eBay."
    )
    parser.add_argument(
        "--query",
        default="soccer card",
        help="Search query to use (default: 'soccer card').",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of result pages to scrape.",
    )
    parser.add_argument(
        "--output",
        default="soccer_card_sales.csv",
        help="Output CSV filename.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between page requests.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    listings = scrape_listings(args.query, args.pages, args.delay)
    write_csv(listings, args.output)
    print(f"Saved {len(listings)} listings to {args.output}")


if __name__ == "__main__":
    main()
