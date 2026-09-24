import http.server
import socketserver
import json
import urllib.parse
import time
import random
import os
import sys

# Ensure UTF-8 output encoding for Windows compatibility
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PORT = 3000

# Global system state in memory
SYSTEM_STATE = {
    "estop_active": False,
    "system_status": "NORMAL", # NORMAL, WARNING, CRITICAL_SHUTDOWN, ESTOP_ENGAGED
    "safety_score": 99.8,
    "uptime_seconds": 184520,
    "config": {
        "safe_threshold_m": 0.50,
        "warn_threshold_m": 0.30,
        "max_hand_speed_ms": 1.2,
        "auto_shutdown_enabled": True
    },
    "t300": {
        "id": "M-T300",
        "name": "T300 Table Saw",
        "rpm": 3450,
        "target_rpm": 3450,
        "distance_m": 0.65,
        "hand_speed_ms": 0.18,
        "zone": "SAFE",
        "guard_status": "ENGAGED",
        "confidence": 99.6,
        "fps": 60,
        "latency_ms": 3.2,
        "power_kw": 2.4,
        "temperature_c": 41.2
    },
    "machines": [
        {
            "id": "M-T300",
            "name": "T300 Table Saw",
            "category": "Cutting",
            "status": "OPERATIONAL",
            "rpm": 3450,
            "max_rpm": 4000,
            "guard": "ENGAGED",
            "power": "ACTIVE",
            "risk_level": "LOW",
            "last_inspection": "Today, 08:00 AM"
        },
        {
            "id": "M-B250",
            "name": "B250 Band Saw",
            "category": "Cutting",
            "status": "OPERATIONAL",
            "rpm": 3200,
            "max_rpm": 3500,
            "guard": "ENGAGED",
            "power": "ACTIVE",
            "risk_level": "LOW",
            "last_inspection": "Today, 08:00 AM"
        },
        {
            "id": "M-R100",
            "name": "R100 Router Table",
            "category": "Milling",
            "status": "OPERATIONAL",
            "rpm": 18000,
            "max_rpm": 24000,
            "guard": "ENGAGED",
            "power": "ACTIVE",
            "risk_level": "LOW",
            "last_inspection": "Yesterday"
        },
        {
            "id": "M-J500",
            "name": "J500 Jointer",
            "category": "Planing",
            "status": "STANDBY",
            "rpm": 0,
            "max_rpm": 5500,
            "guard": "ENGAGED",
            "power": "IDLE",
            "risk_level": "LOW",
            "last_inspection": "Today, 07:30 AM"
        },
        {
            "id": "M-P400",
            "name": "P400 Thickness Planer",
            "category": "Planing",
            "status": "OPERATIONAL",
            "rpm": 5000,
            "max_rpm": 5500,
            "guard": "ENGAGED",
            "power": "ACTIVE",
            "risk_level": "LOW",
            "last_inspection": "Today, 08:00 AM"
        }
    ],
    "incidents": [
        {
            "id": "INC-8891",
            "timestamp": "10 minutes ago",
            "machine": "T300 Table Saw",
            "type": "WARNING",
            "message": "Operator hand entered Warning Zone (22cm from blade). Approach speed 0.85 m/s.",
            "action": "Visual & Audio Caution Signal Dispatched."
        },
        {
            "id": "INC-8890",
            "timestamp": "1 hour ago",
            "machine": "T300 Table Saw",
            "type": "AUTO_STOP",
            "message": "Critical intrusion detected (8.4cm). Instant magnetic brake triggered in 3.1ms.",
            "action": "Machine Shutdown Successful. Operator unharmed."
        },
        {
            "id": "INC-8889",
            "timestamp": "3 hours ago",
            "machine": "R100 Router Table",
            "type": "INFO",
            "message": "Pre-shift optical safety calibration completed successfully.",
            "action": "All sensors verified green."
        }
    ]
}

class WoodSafeHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Dynamically calculate slightly fluctuating telemetry for realism
            t300 = SYSTEM_STATE["t300"]
            if not SYSTEM_STATE["estop_active"] and t300["target_rpm"] > 0:
                t300["rpm"] = min(t300["target_rpm"], max(0, t300["rpm"] + random.randint(-15, 15)))
                t300["confidence"] = round(99.4 + random.uniform(-0.3, 0.4), 1)
            else:
                t300["rpm"] = max(0, int(t300["rpm"] * 0.4)) # Quick spin-down physics
                
            response = {
                "estop_active": SYSTEM_STATE["estop_active"],
                "system_status": SYSTEM_STATE["system_status"],
                "safety_score": SYSTEM_STATE["safety_score"],
                "uptime_seconds": SYSTEM_STATE["uptime_seconds"],
                "active_machines": sum(1 for m in SYSTEM_STATE["machines"] if m["status"] == "OPERATIONAL"),
                "t300": t300,
                "machines": SYSTEM_STATE["machines"],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        elif parsed.path == '/api/incidents':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(SYSTEM_STATE["incidents"]).encode('utf-8'))
            return

        elif parsed.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(SYSTEM_STATE["config"]).encode('utf-8'))
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            body = json.loads(body_bytes.decode('utf-8'))
        except Exception:
            body = {}

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if parsed.path == '/api/estop':
            SYSTEM_STATE["estop_active"] = True
            SYSTEM_STATE["system_status"] = "ESTOP_ENGAGED"
            SYSTEM_STATE["t300"]["target_rpm"] = 0
            SYSTEM_STATE["t300"]["rpm"] = 0
            
            # Halting all machines
            for m in SYSTEM_STATE["machines"]:
                m["status"] = "EMERGENCY_STOPPED"
                m["rpm"] = 0
                m["power"] = "HALTED"
                
            new_incident = {
                "id": f"INC-{random.randint(9000, 9999)}",
                "timestamp": "Just now",
                "machine": body.get("machine", "ALL MACHINES"),
                "type": "EMERGENCY_STOP",
                "message": f"MANUAL EMERGENCY STOP TRIGGERED. All workshop power cut immediately.",
                "action": "Master E-Stop Latching Lock Activated."
            }
            SYSTEM_STATE["incidents"].insert(0, new_incident)
            
            resp = {"status": "success", "estop_active": True, "message": "Emergency Stop engaged across workshop."}
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif parsed.path == '/api/reset':
            SYSTEM_STATE["estop_active"] = False
            SYSTEM_STATE["system_status"] = "NORMAL"
            SYSTEM_STATE["t300"]["target_rpm"] = 3450
            SYSTEM_STATE["t300"]["rpm"] = 3450
            
            for m in SYSTEM_STATE["machines"]:
                if m["id"] == "M-J500":
                    m["status"] = "STANDBY"
                    m["power"] = "IDLE"
                else:
                    m["status"] = "OPERATIONAL"
                    m["power"] = "ACTIVE"
                    if m["id"] == "M-T300": m["rpm"] = 3450
                    elif m["id"] == "M-B250": m["rpm"] = 3200
                    elif m["id"] == "M-R100": m["rpm"] = 18000
                    elif m["id"] == "M-P400": m["rpm"] = 5000

            new_incident = {
                "id": f"INC-{random.randint(9000, 9999)}",
                "timestamp": "Just now",
                "machine": "SYSTEM",
                "type": "INFO",
                "message": "Master Safety Lockout disengaged by authorized operator. System cleared for operation.",
                "action": "All machine safety interlocks verified normal."
            }
            SYSTEM_STATE["incidents"].insert(0, new_incident)

            resp = {"status": "success", "estop_active": False, "message": "System safety reset complete."}
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif parsed.path == '/api/config':
            if "safe_threshold_cm" in body:
                SYSTEM_STATE["config"]["safe_threshold_cm"] = float(body["safe_threshold_cm"])
            if "warn_threshold_cm" in body:
                SYSTEM_STATE["config"]["warn_threshold_cm"] = float(body["warn_threshold_cm"])
            if "stop_threshold_cm" in body:
                SYSTEM_STATE["config"]["stop_threshold_cm"] = float(body["stop_threshold_cm"])
                
            resp = {"status": "success", "config": SYSTEM_STATE["config"]}
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

if __name__ == '__main__':
    print(f"==================================================")
    print(f"🛡️  WoodSafe Guardian AI Safety Server Started")
    print(f"📍  Listening at: http://localhost:{PORT}")
    print(f"==================================================")
    with socketserver.TCPServer(("", PORT), WoodSafeHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down WoodSafe Guardian server.")
