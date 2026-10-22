# ParkPilot — Smart Mall Parking System

**Find an available space. Select it. Follow the route.**

ParkPilot is a hackathon prototype that connects a parking-space sensor to an interactive mobile-friendly website. Drivers can view spaces by floor, select an available bay, and follow an illustrated route from the parking-floor entrance. The project also demonstrates how nearby parking alternatives could be presented when the mall is full.

**Team:** We Though This Was a Food Competition  
**University:** Xiamen University Malaysia

![ParkPilot running on a phone](docs/images/parking-app-on-phone.jpg)

## What we built

- **Live sensor input:** Arduino Uno CH340 reads a photoresistor (LDR) and sends `S1,<reading>` over USB serial.
- **Python server:** Flask receives readings on the laptop (default `COM13`) and calculates parking availability.
- **Mobile website:** View totals, floors, occupied/available bays, and example nearby buildings.
- **Indoor guidance demonstration:** Tap a green bay to draw a suggested blue route on an illustrated floor map; manually advance through navigation steps.
- **Public demo option:** Serve a read-only customer site through a temporary Cloudflare Tunnel link so phones on mobile data can access it.

| Interactive parking map | Physical sensor prototype |
| --- | --- |
| ![Indoor parking map](docs/images/indoor-navigation-map.png) | ![Arduino and photoresistor](docs/images/arduino-ldr-prototype.jpg) |

> **Prototype limitations:** Only **Ground Floor A01 (`M-A01`)** uses a real physical sensor. Other bays and nearby-building occupancy values are **simulated**. The illustrated driving map is a **sample layout**, not a surveyed mall floor plan; moving route steps are a **manual demonstration**, not actual GPS or real-time indoor tracking. The photoresistor measures light, so it is not a production-grade vehicle detector.

## System overview

```text
Photoresistor (LDR)
        |
Arduino Uno CH340  --USB serial (9600 baud)-->  Python / Flask server
                                                    |
                                       Parking counts + status API
                                                    |
                                      HTML / CSS / JavaScript map
                                                    |
                                        Laptop or phone browser
                                                    |
                                  Cloudflare Tunnel (optional)
                                                    |
                                     Remote phone on mobile data
```

## Repository structure

```text
Smart-Mall-Parking-System/
├── app.py                      # Flask server and parking data/API
├── public_server.py            # Read-only server via Waitress
├── requirements.txt            # Python dependencies
├── arduino/
│   └── parking_sensor.ino      # Arduino LDR sensor sketch
├── templates/
│   └── index.html              # Website layout
├── static/
│   ├── app.js                  # Interactive map/navigation
│   └── style.css               # Responsive styling
├── START_PUBLIC_WEBSITE.bat    # Windows: run read-only website
├── START_PUBLIC_LINK.bat       # Windows: create temporary URL
├── RUN_PARKING.bat             # Windows: local demo server
├── docs/
│   ├── images/                # Prototype images
│   ├── UPLOAD_TO_GITHUB.md    # Upload instructions
│   └── DEMO_NOTES.md          # Notes for judges
└── tests/
    └── test_app.py            # Backend smoke tests
```

## Quick start — Windows

**Requirements:** Python 3.10+ and an Arduino Uno-compatible board (CH340) if using the physical sensor.

1. Connect the Arduino via USB. In Arduino IDE, select **Arduino Uno**, the correct COM port, and upload `arduino/parking_sensor.ino` if you have not already uploaded the same `S1,<value>` sketch.
2. Connect the LDR as a voltage divider: `5V → LDR → (A0 junction) → 10 kΩ resistor → GND`. An analog input wire connects the junction to `A0`.
3. Close **Arduino Serial Monitor** before starting Python; only one program can open the COM port at a time.
4. Open a terminal in the repository folder and install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Review the configuration near the top of `app.py`:

   ```python
   SERIAL_ENABLED = True
   SERIAL_PORT = "COM13"       # Change if your Arduino uses a different port
   BAUD_RATE = 9600
   SENSOR_THRESHOLD = 500     # Calibrate with your LDR
   OCCUPIED_WHEN = "below"    # For 5V → LDR → A0 → 10kΩ → GND
   ```

6. Start the **local demo** server (which permits manual demo-space toggles):

   ```powershell
   python app.py
   ```

7. Open **http://127.0.0.1:5000** in your laptop browser.

For a no-hardware website demo, set `SERIAL_ENABLED = False` in `app.py`. This keeps the sample spaces and map available but does **not** provide live sensor readings.

## Optional: Phone access over the internet

For a **temporary, read-only** public demo, stop the local Flask server first, then:

1. Run **`START_PUBLIC_WEBSITE.bat`**. It starts the website using Waitress on `127.0.0.1:5000` with demo edits disabled.
2. Install Cloudflare Tunnel if necessary: `winget install -e --id Cloudflare.cloudflared`.
3. Run **`START_PUBLIC_LINK.bat`**. Copy the generated `https://...trycloudflare.com` link.
4. Open the link on a phone using mobile data.

Your laptop, Arduino (for live sensor data), Python server, internet connection, and tunnel must remain running. Quick Tunnel links are temporary and may change after a restart.

**Do not expose `python app.py` directly to the public internet.** Use the provided read-only public server for the hackathon demo. Details: [`PUBLIC_HOSTING_GUIDE.md`](PUBLIC_HOSTING_GUIDE.md).

## Future development

The sensing layer is flexible: a real deployment could use infrared, ultrasonic, magnetic, or purpose-built vehicle-presence sensors instead of an LDR. The team also proposes Wi-Fi/Bluetooth-based **indoor positioning infrastructure** so a customer's phone can estimate its location and navigate inside underground parking levels without relying on satellite GPS reception. This is a proposed enhancement, **not a feature implemented in the current prototype**. A real installation also requires an accurate floor plan and a verified parking-data feed from nearby buildings.

## Team

- **Yeow Teck Jian** — Team leader
- Gay Hao Jie
- Haw San Jen
- Chong Jing Ze
- Chew Xu Jie

All team members are students at **Xiamen University Malaysia**.

## Tests

```powershell
python -m unittest discover -s tests -v
```

See [`docs/DEMO_NOTES.md`](docs/DEMO_NOTES.md) for a quick presentation checklist.
