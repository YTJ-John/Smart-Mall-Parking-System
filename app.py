from flask import Flask, jsonify, render_template, request
from threading import Thread, Lock
import time
import os

try:
    import serial
except ImportError:
    serial = None

app = Flask(__name__)

# CHANGE THESE SETTINGS FOR YOUR COMPUTER AND SENSOR
SERIAL_ENABLED = True
PUBLIC_READ_ONLY = os.environ.get("PUBLIC_READ_ONLY", "0") == "1"
SERIAL_PORT = "COM13"       # Windows: COM3/COM4; macOS/Linux use their device path
BAUD_RATE = 9600
SENSOR_THRESHOLD = 500     # Calibrate from actual bright/dark readings
OCCUPIED_WHEN = "below"    # With the recommended LDR divider, dark = occupied

lock = Lock()
last_sensor_value = None
serial_status = "Serial reader has not started"
last_update = None

# S1 is the one physical sensor. Remaining slots are sample/demo values.
parking = {
    "mall": {
        "name": "Main Mall",
        "areas": {
            "Ground Floor": [
                {"id": "M-A01", "sensor": "S1", "occupied": False, "source": "sensor"},
                {"id": "M-A02", "sensor": None, "occupied": True,  "source": "demo"},
                {"id": "M-A03", "sensor": None, "occupied": False, "source": "demo"},
                {"id": "M-A04", "sensor": None, "occupied": True,  "source": "demo"},
                {"id": "M-A05", "sensor": None, "occupied": False, "source": "demo"},
            ],
            "Level 1": [
                {"id": "M-B01", "sensor": None, "occupied": True,  "source": "demo"},
                {"id": "M-B02", "sensor": None, "occupied": False, "source": "demo"},
                {"id": "M-B03", "sensor": None, "occupied": False, "source": "demo"},
                {"id": "M-B04", "sensor": None, "occupied": True,  "source": "demo"},
                {"id": "M-B05", "sensor": None, "occupied": False, "source": "demo"},
            ],
            "Rooftop": [
                {"id": "M-C01", "sensor": None, "occupied": True,  "source": "demo"},
                {"id": "M-C02", "sensor": None, "occupied": True,  "source": "demo"},
                {"id": "M-C03", "sensor": None, "occupied": False, "source": "demo"},
                {"id": "M-C04", "sensor": None, "occupied": False, "source": "demo"},
                {"id": "M-C05", "sensor": None, "occupied": False, "source": "demo"},
            ],
        },
    },
    "nearby": [
        {"id": "B1", "name": "Office Tower Parking", "distance": "Sample distance", "destination": "",
         "areas": {"Basement": [
             {"id": "OT-B01", "occupied": False}, {"id": "OT-B02", "occupied": True},
             {"id": "OT-B03", "occupied": False}, {"id": "OT-B04", "occupied": False}]}},
        {"id": "B2", "name": "City Centre Parking", "distance": "Sample distance", "destination": "",
         "areas": {"Level 1": [
             {"id": "CC-L1-01", "occupied": True}, {"id": "CC-L1-02", "occupied": False},
             {"id": "CC-L1-03", "occupied": False}, {"id": "CC-L1-04", "occupied": True}]}},
        {"id": "B3", "name": "Hotel Parking", "distance": "Sample distance", "destination": "",
         "areas": {"Basement": [
             {"id": "HP-B01", "occupied": False}, {"id": "HP-B02", "occupied": False},
             {"id": "HP-B03", "occupied": True}]}},
    ],
}


def is_occupied(value):
    return value < SENSOR_THRESHOLD if OCCUPIED_WHEN == "below" else value > SENSOR_THRESHOLD


def all_mall_slots():
    for area_name, slots in parking["mall"]["areas"].items():
        for slot in slots:
            yield area_name, slot


def summarize_slots(slots):
    total = len(slots)
    available = sum(1 for slot in slots if not slot["occupied"])
    return {"available": available, "total": total, "occupied": total - available}


def serial_reader():
    global last_sensor_value, serial_status, last_update
    if not SERIAL_ENABLED:
        serial_status = "Serial disabled — demo mode"
        return
    if serial is None:
        serial_status = "pyserial is not installed"
        return

    while True:
        try:
            serial_status = f"Connecting to {SERIAL_PORT}..."
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                time.sleep(2)  # Arduino may reset when serial opens
                serial_status = f"Connected to {SERIAL_PORT}"
                while True:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    parts = raw.split(",")
                    if len(parts) != 2:
                        continue
                    sensor_id = parts[0].strip()
                    try:
                        value = int(parts[1].strip())
                    except ValueError:
                        continue
                    with lock:
                        last_sensor_value = value
                        last_update = time.strftime("%Y-%m-%d %H:%M:%S")
                        for _, slot in all_mall_slots():
                            if slot.get("sensor") == sensor_id:
                                slot["occupied"] = is_occupied(value)
                                slot["source"] = "sensor"
        except Exception as exc:
            serial_status = f"Serial unavailable: {exc}"
            time.sleep(3)


def get_dashboard_data():
    areas = []
    mall_total = mall_available = 0
    for area_name, slots in parking["mall"]["areas"].items():
        summary = summarize_slots(slots)
        mall_total += summary["total"]
        mall_available += summary["available"]
        areas.append({
            "name": area_name, **summary,
            "slots": [{"id": s["id"], "occupied": s["occupied"], "source": s["source"]} for s in slots],
        })

    nearby = []
    for building in parking["nearby"]:
        all_slots = [slot for area_slots in building["areas"].values() for slot in area_slots]
        area_summaries = [
            {"name": name, **summarize_slots(slots)}
            for name, slots in building["areas"].items()
        ]
        nearby.append({
            "id": building["id"], "name": building["name"], "distance": building["distance"],
            "destination": building.get("destination", ""),
            **summarize_slots(all_slots), "areas": area_summaries,
        })

    return {
        "mall": {"name": parking["mall"]["name"], "available": mall_available,
                 "total": mall_total, "areas": areas},
        "nearby": nearby,
        "sensor": {"enabled": SERIAL_ENABLED, "status": serial_status,
                   "last_value": last_sensor_value, "last_update": last_update,
                   "threshold": SENSOR_THRESHOLD, "occupied_when": OCCUPIED_WHEN},
        "updated_at": time.strftime("%H:%M:%S"),
        "read_only": PUBLIC_READ_ONLY,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parking")
def api_parking():
    with lock:
        return jsonify(get_dashboard_data())


@app.route("/api/demo/toggle", methods=["POST"])
def demo_toggle():
    if PUBLIC_READ_ONLY:
        return jsonify({"ok": False, "error": "Public website is read-only. Only the demo operator can change sample parking counts."}), 403
    payload = request.get_json(silent=True) or {}
    slot_id = payload.get("slot_id")
    for _, slot in all_mall_slots():
        if slot["id"] == slot_id and slot["source"] == "demo":
            with lock:
                slot["occupied"] = not slot["occupied"]
                return jsonify({"ok": True, "slot_id": slot_id, "occupied": slot["occupied"]})
    return jsonify({"ok": False, "error": "Only sample/demo mall slots can be toggled here."}), 400


if __name__ == "__main__":
    if SERIAL_ENABLED:
        Thread(target=serial_reader, daemon=True).start()
    else:
        serial_status = "Serial disabled — demo mode"
    app.run(host="0.0.0.0", port=5000, debug=False)
