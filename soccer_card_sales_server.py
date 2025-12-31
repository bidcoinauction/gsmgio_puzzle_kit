#!/usr/bin/env python3
"""Serve a simple front-end for scraping sold soccer card listings."""

from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEFAULT_HTML = Path(__file__).with_name("soccer_card_sales_frontend.html")


class SoccerCardSalesHandler(BaseHTTPRequestHandler):
    server_version = "SoccerCardSales/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            self.handle_search(parsed)
            return
        if parsed.path == "/":
            self.serve_file(DEFAULT_HTML)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def handle_search(self, parsed) -> None:
        params = parse_qs(parsed.query)
        query = params.get("query", ["soccer card"])[0]
        pages = clamp_int(params.get("pages", ["1"])[0], minimum=1, maximum=10)
        delay = clamp_float(params.get("delay", ["1"])[0], minimum=0.0, maximum=10.0)

        from scrape_soccer_card_sales import scrape_listings

        listings = scrape_listings(query, pages, delay)
        payload = {
            "query": query,
            "pages": pages,
            "delay": delay,
            "count": len(listings),
            "listings": [listing_to_dict(listing) for listing in listings],
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path: Path) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        content = path.read_bytes()
        content_type, _ = mimetypes.guess_type(path.name)
        if not content_type:
            content_type = "text/plain"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:
        return


def clamp_int(value: str, *, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except ValueError:
        return minimum
    return max(minimum, min(parsed, maximum))


def clamp_float(value: str, *, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except ValueError:
        return minimum
    return max(minimum, min(parsed, maximum))


def listing_to_dict(listing) -> dict:
    return {
        "title": listing.title,
        "price": f"{listing.price}" if listing.price is not None else None,
        "shipping": f"{listing.shipping}" if listing.shipping is not None else None,
        "total": f"{listing.total}" if listing.total is not None else None,
        "sold_date": listing.sold_date,
        "url": listing.url,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve a front-end for scraping sold soccer card listings."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host interface to bind (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = HTTPServer((args.host, args.port), SoccerCardSalesHandler)
    print(f"Serving on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
