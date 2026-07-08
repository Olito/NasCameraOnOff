#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timedelta, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "camera_pause_state.json")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"active": False, "until": None}
    return {"active": False, "until": None}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def pause(hours):
    try:
        hours = float(hours)
    except ValueError:
        print("Horas inválidas")
        sys.exit(2)

    if hours <= 0:
        print("Debes indicar un valor mayor que 0")
        sys.exit(2)

    now = datetime.now(timezone.utc)
    until = now + timedelta(hours=hours)

    state = {
        "active": True,
        "started_at": now.isoformat(),
        "until": until.isoformat(),
        "hours": hours,
    }
    save_state(state)

    print(f"Pausa activada durante {hours} hora(s)")
    print(f"Finaliza en: {until.isoformat()}")


def resume():
    state = {"active": False, "until": None, "started_at": None, "hours": None}
    save_state(state)
    print("Pausa cancelada")


def status():
    state = load_state()
    if not state.get("active"):
        print("Sin pausa activa")
        return

    until = datetime.fromisoformat(state["until"])
    now = datetime.now(timezone.utc)

    if now >= until:
        save_state({"active": False, "until": None, "started_at": None, "hours": None})
        print("La pausa ha expirado")
        return

    remaining = until - now
    minutes = int(remaining.total_seconds() // 60)
    print(f"Pausa activa. Quedan {minutes} minutos")


def check():
    state = load_state()
    if not state.get("active"):
        print("allow")
        sys.exit(0)

    until = datetime.fromisoformat(state["until"])
    now = datetime.now(timezone.utc)

    if now >= until:
        save_state({"active": False, "until": None, "started_at": None, "hours": None})
        print("allow")
        sys.exit(0)

    print("block")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 camera_pause.py pause 3")
        print("  python3 camera_pause.py pause 6.5")
        print("  python3 camera_pause.py resume")
        print("  python3 camera_pause.py status")
        print("  python3 camera_pause.py check")
        sys.exit(2)

    action = sys.argv[1].lower()

    if action == "pause":
        if len(sys.argv) < 3:
            print("Falta el número de horas")
            sys.exit(2)
        pause(sys.argv[2])

    elif action == "resume":
        resume()

    elif action == "status":
        status()

    elif action == "check":
        check()

    else:
        print("Acción no reconocida")
        sys.exit(2)