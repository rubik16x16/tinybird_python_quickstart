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


class EventsView:
    def get(self, query_params):
        print(f"Received GET request with query params: {query_params}")
        return {"data": "Events view"}

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

        # tinybird.ecommerce_events.ingest(valid_events)

        response = {
            "total_events": len(data["events"]),
            "count_valid_events": len(valid_events),
            "count_invalid_events": len(invalid_events),
            "count_duplicate_events": duplicate_events,
            "invalid_events": invalid_events,
            "valid_events": valid_events,
        }

        return response


routes = {
    "/api/events": EventsView,
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
