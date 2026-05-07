import json
from collections import Counter
from datetime import datetime
from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, Field, ValidationError

from src.tinybird.client import tinybird


class EventType(str, Enum):
    PRODUCT_VIEW = "product_view"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"


class Event(BaseModel):
    event_id: int
    user_id: int
    event_type: EventType
    product_id: int
    timestamp: datetime
    price: float = Field(gt=0)
    country: str


class GetMetricsView:
    def get(self, query_params):

        start_date = query_params.get("start_date", ["2026-01-01 00:00:00"])[0]
        end_date = query_params.get("end_date", ["2026-12-31 23:59:59"])[0]
        country = query_params.get("country", ["VE"])[0]

        ecommerce_summary_result = tinybird.ecommerce_summary.query(
            {
                "start_date": start_date,
                "end_date": end_date,
                "country": country,
            }
        )

        ecommerce_top_products_result = tinybird.ecommerce_top_products.query(
            {
                "start_date": start_date,
                "end_date": end_date,
                "country": country,
            }
        )

        sumary_metrics = {
            "total_revenue": ecommerce_summary_result["data"][0]["total_revenue"],
            "purchases": ecommerce_summary_result["data"][0]["purchases"],
            "product_views": ecommerce_summary_result["data"][0]["product_views"],
            "unique_users": ecommerce_summary_result["data"][0]["unique_users"],
        }

        if sumary_metrics["product_views"] > 0:
            sumary_metrics["conversion_rate"] = (
                sumary_metrics["purchases"] / sumary_metrics["product_views"]
            )
        else:
            sumary_metrics["conversion_rate"] = 0

        top_products = [
            {
                "product_id": row["product_id"],
                "purchase_count": row["purchase_count"],
                "revenue": row["revenue"],
            }
            for row in ecommerce_top_products_result["data"]
        ]

        return {
            "data": {
                "start_date": start_date,
                "end_date": end_date,
                "country": country,
                "summary": sumary_metrics,
                "top_products": top_products,
            }
        }


class EventsView:

    def post(self, data):
        valid_events = []
        invalid_events = []
        event_ids = [event_data["event_id"] for event_data in data["events"]]
        id_counts = Counter(event_ids)
        duplicate_events = sum(c - 1 for c in id_counts.values() if c > 1)

        for event_data in data["events"]:
            try:
                event = Event(**event_data)
                print(f"Validated event: {event}")
                valid_events.append(event_data)
            except ValidationError as e:
                invalid_events.append({"event": event_data, "errors": e.errors()})

        for event in valid_events:
            print(f"Ingesting event: {event}")
            tinybird.ecommerce_events.ingest(event)

        response = {
            "data": {
                "total_events": len(data["events"]),
                "count_valid_events": len(valid_events),
                "count_invalid_events": len(invalid_events),
                "count_duplicate_events": duplicate_events,
                "invalid_events": invalid_events,
                "valid_events": valid_events,
            }
        }

        return response


routes = {
    "/api/events": EventsView,
    "/api/get_metrics": GetMetricsView,
}


class SimpleAPIHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):

        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path in routes:
            view = routes[path]()
            query_params = parse_qs(parsed_url.query)
            response = view.get(query_params)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if self.path in routes:

            view = routes[path]()
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            response = view.post(data)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
            return
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


def run_server(port=8000):

    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    print(f"🚀 Server running on http://localhost:{port}")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
