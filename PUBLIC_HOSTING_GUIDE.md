# Smart Mall Parking — Public Phone Access (Hackathon)

This is the existing indoor-navigation parking app adapted for **temporary public phone access**. It uses your existing Arduino Uno CH340 on **COM13** and photoresistor sketch. Only **M-A01** has a physical sensor; other parking spaces and nearby-building counts remain **demo data**.

## QUICK SETUP — Windows

1. **Keep your previous working folder** as a backup. Extract this ZIP to a separate folder.
2. In `app.py`, confirm `SERIAL_PORT = "COM13"`, `SENSOR_THRESHOLD` (use your measured/calibrated threshold), and `OCCUPIED_WHEN` (typically `"below"` for LDR wired to 5V with 10kΩ to ground).
3. Close the Arduino Serial Monitor, old Python app/server, and anything else using COM13 or port 5000.
4. Double-click **`START_PUBLIC_WEBSITE.bat`**. It installs Python requirements and runs the app using **Waitress** listening on **127.0.0.1:5000**, not exposed directly to the network. If Python is not found, install Python and check PATH. If packages were already installed, it reuses them.
5. On the **same laptop**, test `http://127.0.0.1:5000`. The sensor status should read **Connected to COM13** after a short delay. If not, check the port and that Serial Monitor is closed.
6. Install **Cloudflare Tunnel (`cloudflared`)** on Windows using a Command Prompt or Terminal:
   ```cmd
   winget install -e --id Cloudflare.cloudflared
   ```
   Then **close/reopen Command Prompt** or log out/in if the executable is not found. Documentation: https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
7. Double-click **`START_PUBLIC_LINK.bat`**, or in a second Command Prompt run:
   ```cmd
   cloudflared tunnel --url http://127.0.0.1:5000
   ```
8. Look for a random `https://...trycloudflare.com` address in the tunnel window. Copy **that exact link** to your phone. Open it using **mobile data**, even if the phone is not on your laptop's Wi-Fi. The public site is HTTPS. Share it with judges or customers only for your hackathon test.

**Keep both black windows running and the computer awake.** When you close the tunnel, the temporary public URL stops working. Reopening the tunnel may generate a different address. You cannot pre-choose the temporary link or keep it fixed with this method. It is a temporary testing service, not permanent hosting.

## Why two windows?
- **START_PUBLIC_WEBSITE.bat** reads your Arduino on COM13, calculates availability, and serves the map app from your laptop using a Windows-compatible WSGI server.
- **START_PUBLIC_LINK.bat** connects Cloudflare to that local website. There is no change to the Arduino firmware.

## Public safety
- This public edition is **read-only to visitors**: the indoor map, selectable empty bays, and guided route remain interactive, but the buttons that would change fake/demo occupancy are disabled. The `/api/demo/toggle` server endpoint also refuses POST requests when the public server runs.
- Your original `python app.py` local mode still supports demo occupancy editing. Do NOT tunnel that original development-mode server publicly; only tunnel **public_server.py**.
- **Anyone who receives the tunnel URL may view the map and live sample sensor readings.** Do not expose private data, other internal services or real user information.
- Only one physical bay is measured by your LDR. Sample counts are explicitly illustrative, not actual mall data.
- Tunnel TLS protects the web connection but does not mean the web app is independently security audited. Use this for supervised hackathon demonstration, not a real commercial parking system.

## Troubleshooting
- **'python' is not recognized**: install Python and select Add to PATH during setup; use `py` instead of `python` where appropriate.
- **'cloudflared' is not recognized**: reinstall with winget and reopen Command Prompt (PATH update).
- **Already using port 5000**: stop the old server with Ctrl+C or close its terminal.
- **COM13 unavailable**: close Arduino Serial Monitor; check the Arduino USB cable and port in Device Manager.
- **Phone can't open link**: leave both windows open, check the URL printed by cloudflared, test the local URL, make sure laptop has internet access.
- **Map works but doesn't update**: confirm sensor connection state, readings, and threshold at bottom of page.

## Future permanent hosting
For a stable permanent website/domain, use a named Cloudflare Tunnel or a cloud-hosted Flask service and a separate Arduino-to-cloud uploader. A remotely hosted server **cannot directly open the COM13 port on your laptop**. For a later permanent version, publish sensor readings from the laptop securely to a hosted backend over HTTPS and configure authentication and persistence.
