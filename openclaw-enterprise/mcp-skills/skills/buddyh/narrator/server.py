#!/usr/bin/env python3
"""
Narrator Socket Server
Listens on /tmp/narrator_socket.sock for screenshot analysis requests.
"""

import socket
import struct
import json
import os
import sys

SOCKET_PATH = '/tmp/narrator_socket.sock'

def analyze_screenshot(png_bytes, app_name, window_title):
    """
    Send to Clawdbot skill for analysis.
    Returns a narration line.
    """
    # This would call the narrator skill
    # For now, return a placeholder
    return "And they're looking at... absolutely nothing! The narrator isn't running yet!"

def handle_client(conn):
    """Handle incoming connection."""
    try:
        # Read PNG size (4 bytes, big-endian)
        size_data = conn.recv(4)
        if len(size_data) < 4:
            return
        png_size = struct.unpack('>I', size_data)[0]
        
        # Read PNG bytes
        png_bytes = b''
        while len(png_bytes) < png_size:
            chunk = conn.recv(min(8192, png_size - len(png_bytes)))
            png_bytes += chunk
        
        # Read app name (newline-terminated)
        app_name = b''
        while not app_name.endswith(b'\n'):
            chunk = conn.recv(1)
            if not chunk:
                break
            app_name += chunk
        app_name = app_name.decode('utf-8').strip()
        
        # Read window title (newline-terminated)
        window_title = b''
        while not window_title.endswith(b'\n'):
            chunk = conn.recv(1)
            if not chunk:
                break
            window_title += chunk
        window_title = window_title.decode('utf-8').strip()
        
        # Analyze and get narration
        narration = analyze_screenshot(png_bytes, app_name, window_title)
        
        # Send back narration
        conn.sendall(narration.encode('utf-8'))
        
    except Exception as e:
        print(f"Error handling client: {e}", file=sys.stderr)
    finally:
        conn.close()

def main():
    """Start the socket server."""
    # Clean up old socket
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(SOCKET_PATH)
    server.listen(5)
    
    print(f"📺 Narrator server listening on {SOCKET_PATH}", file=sys.stdout)
    
    while True:
        conn, _ = server.accept()
        handle_client(conn)

if __name__ == '__main__':
    main()
