#!/usr/bin/env python3
"""
Simple HTTP server to serve the HTML interface for the Law Firm AI application.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8080

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # Change to the directory containing the HTML file
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 Web interface server running at: http://localhost:{PORT}")
        print(f"📁 Serving files from: {web_dir}")
        print(f"🔗 Open http://localhost:{PORT}/test_form.html to use the interface")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.shutdown()