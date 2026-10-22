"""Local serial-backed read-only server for Cloudflare Tunnel.

Run this on the Windows laptop that is connected to the Arduino on COM13.
The public HTTPS connection is provided by Cloudflare Tunnel, not by Waitress.
"""
import os
os.environ["PUBLIC_READ_ONLY"] = "1"  # always disable public editing

from threading import Thread
from waitress import serve
import app as parking

if __name__ == "__main__":
    if parking.SERIAL_ENABLED:
        Thread(target=parking.serial_reader, daemon=True).start()
    else:
        parking.serial_status = "Serial disabled — demo mode"

    print("Parking server: http://127.0.0.1:5000", flush=True)
    print("In a SECOND Command Prompt, run: cloudflared tunnel --url http://127.0.0.1:5000", flush=True)
    serve(parking.app, host="127.0.0.1", port=5000, threads=8)
