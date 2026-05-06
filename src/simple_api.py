from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class EventsView:
    def get(self):
        return {"data": "Events view"}

    def post(self, data):
        print(f"Received data: {data}")
        return {"data": "Events view"}


routes = {
    "/api/events": EventsView,
}


class SimpleAPIHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):

        if self.path in routes:
            view = routes[self.path]()
            response = view.get()
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):

        if self.path in routes:
            view = routes[self.path]()
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            response = view.post(data)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
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
