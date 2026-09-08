#!/usr/bin/env python3
"""Multi-port TCP listener + mock server for game protocol capture.

Listens on multiple ports simultaneously, logs all data, sends mock responses.
Designed for Cocos2d-x LuaSocket games.

Usage:
  python3 mock-server.py [--ports 8080,80,443,7777,8888,9999,4444]
"""
import asyncio
import sys
import os
import json
from datetime import datetime

LOG_DIR = "capture-logs"

class GameProtocolHandler:
    """Analyzes captured game protocol data and generates mock responses."""

    def __init__(self):
        self.sessions = {}

    async def handle_client(self, reader, writer, port):
        addr = writer.get_extra_info('peername')
        session_id = f"{addr[0]}:{addr[1]}"
        print(f"[+] Connection on port {port} from {session_id}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logfile = os.path.join(LOG_DIR, f"port_{port}_{timestamp}.bin")

        data_all = bytearray()
        try:
            while True:
                data = await asyncio.wait_for(reader.read(4096), timeout=30)
                if not data:
                    break
                data_all.extend(data)
                print(f"  <<< [{port}] recv {len(data)} bytes: {data[:64].hex()}")

                # Try to identify protocol type
                self.analyze_packet(data, port)

                # Send mock response
                response = self.generate_mock_response(data, port)
                if response:
                    print(f"  >>> [{port}] send {len(response)} bytes")
                    writer.write(response)
                    await writer.drain()

        except asyncio.TimeoutError:
            print(f"  [!] Timeout on port {port}")
        except ConnectionResetError:
            print(f"  [!] Connection reset on port {port}")
        except Exception as e:
            print(f"  [!] Error on port {port}: {e}")
        finally:
            with open(logfile, 'wb') as f:
                f.write(data_all)
            print(f"  [*] Logged {len(data_all)} bytes to {logfile}")
            writer.close()

    def analyze_packet(self, data, port):
        """Try to identify what protocol the game is using."""
        if len(data) < 4:
            return

        # Check for HTTP/WebSocket
        if data.startswith(b'GET ') or data.startswith(b'POST '):
            print(f"  [proto] HTTP request detected")
        elif data.startswith(b'\x16\x03'):  # TLS
            print(f"  [proto] TLS handshake detected")
        elif len(data) > 8:
            # Check for length-prefixed protocol (common in games)
            if len(data) >= 4:
                pkt_len = int.from_bytes(data[0:4], 'big')
                print(f"  [proto] Possible length-prefixed protocol: len={pkt_len}")

    def generate_mock_response(self, data, port):
        """Generate mock responses based on protocol patterns."""
        # If it looks like HTTP, return a simple HTTP response
        if data.startswith(b'GET /'):
            return b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"

        # For unknown protocols, echo back or return empty
        # Most game servers expect specific binary responses
        return None  # Don't respond, just observe


async def main(ports):
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"[*] Starting mock server on ports: {ports}")
    print(f"[*] Log dir: {LOG_DIR}")

    handler = GameProtocolHandler()

    servers = []
    for port in ports:
        try:
            server = await asyncio.start_server(
                lambda r, w, p=port: handler.handle_client(r, w, p),
                '0.0.0.0', port)
            servers.append(server)
            print(f"  [*] Listening on port {port}")
        except OSError as e:
            print(f"  [!] Cannot bind port {port}: {e}")

    if not servers:
        print("[!] No ports could be bound!")
        sys.exit(1)

    print(f"\n[*] Ready! Use: adb reverse tcp:<PORT> tcp:<PORT>")
    print("[*] Waiting for connections...\n")

    await asyncio.gather(*(s.serve_forever() for s in servers))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Game Protocol Mock Server')
    parser.add_argument('--ports', type=str, default='8080,80,443,7777,8888,9999,4444,3000,4000,5000,6000,7000,9000',
                        help='Comma-separated list of ports to listen on')
    args = parser.parse_args()

    ports = [int(p.strip()) for p in args.ports.split(',')]
    asyncio.run(main(ports))
