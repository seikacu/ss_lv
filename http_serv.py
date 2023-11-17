# importing required modules.
import http.server, socketserver
# configuring port number.
PORT = 51000
# inheriting from http.server.SimpleHTTPRequestHandler
class MyHandler(http.server.SimpleHTTPRequestHandler):


def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(b"Serving From Python http.server module.")
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("serving at port", PORT)
        # this will start the server.
        httpd.serve_forever()