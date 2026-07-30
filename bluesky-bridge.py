# ================================================================
#  BlueSky External Bridge
#  Version: 3.0
#  Reads:
#    • ZMQ port 11000  — BlueSky core ACDATA  (lat/lon/alt/gs/vs/hdg/trk/ias/mach/type)
#    • ZMQ port 11005  — ATC_EXTRAS plugin    (squawk/situation/ident/orig/dest/nextwp/eta/sim_time)
#  Publishes:
#    • WebSocket port 8080 — merged flat JSON every SEND_INTERVAL seconds
# ================================================================

import zmq
import msgpack
import numpy as np
import threading
import time
import json
import asyncio
import websockets
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("BlueSkyBridge")

# ---- Configuration ----
ZMQ_CORE_HOST   = "tcp://localhost:11000"
ZMQ_EXTRAS_HOST = "tcp://localhost:11005"
WS_HOST         = "0.0.0.0"
WS_PORT         = 8080
SEND_INTERVAL   = 0.5          # seconds between WebSocket pushes
# -----------------------

# Shared state
latest_aircraft: list  = []    # list of aircraft dicts, rebuilt each ACDATA frame
extra_cache:     dict  = {}    # keyed by callsign string
data_lock = threading.Lock()


# ==================================================================
# Helper: decode BlueSky's msgpack numpy-encoded arrays
# ==================================================================
def _decode_numpy(val):
    """Return a plain Python float or list from a BlueSky numpy-encoded dict."""
    if isinstance(val, dict) and val.get(b"numpy"):
        dtype = np.dtype(val[b"type"])
        arr   = np.frombuffer(val[b"data"], dtype=dtype)
        return float(arr[0]) if arr.size == 1 else arr.tolist()
    return val


def _get_float(field, idx: int, default: float = 0.0) -> float:
    decoded = _decode_numpy(field)
    if isinstance(decoded, list):
        return float(decoded[idx]) if idx < len(decoded) else default
    if isinstance(decoded, (int, float)):
        return float(decoded)
    return default


def _get_str(field, idx: int, default: str = "") -> str:
    decoded = _decode_numpy(field)
    if isinstance(decoded, list):
        if idx < len(decoded):
            v = decoded[idx]
            return v.decode("utf-8") if isinstance(v, bytes) else str(v)
    return default


# ==================================================================
# WTC classifier
# ==================================================================
_HEAVY = {"B744","B748","B741","B742","B772","B773","B77L","B77W",
          "A333","A343","A345","A346","A359","A35K","A388","B747",
          "A380","B777","B787","A350","C5","AN124","IL76"}
_LIGHT = {"C150","C152","C172","C182","DA20","DA40","DA42",
          "PA28","PA34","SR20","SR22","C208","PC12"}

def get_wtc(ac_type: str) -> str:
    if not ac_type:
        return "-"
    t = ac_type.upper()
    if t in _HEAVY: return "H"
    if t in _LIGHT: return "L"
    return "M"


# ==================================================================
# Thread 1 — ZMQ subscriber for ATC_EXTRAS plugin data (port 11005)
# ==================================================================
def thread_extras_reader():
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt_string(zmq.SUBSCRIBE, "EXTRADATA")
    sub.connect(ZMQ_EXTRAS_HOST)
    logger.info(f"[EXTRAS] Subscribed to {ZMQ_EXTRAS_HOST}")

    while True:
        try:
            msg   = sub.recv_string()
            parts = msg.split(" ", 1)
            if len(parts) != 2:
                continue
            parsed = json.loads(parts[1])
            with data_lock:
                extra_cache.update(parsed)   # preserves sim_time key
        except Exception as exc:
            logger.error(f"[EXTRAS] {exc}")


# ==================================================================
# Thread 2 — ZMQ subscriber for BlueSky core ACDATA (port 11000)
# ==================================================================
def thread_core_reader():
    global latest_aircraft
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, b"")
    sub.setsockopt(zmq.RCVTIMEO, 1000)
    sub.connect(ZMQ_CORE_HOST)
    logger.info(f"[CORE] Subscribed to {ZMQ_CORE_HOST}")

    while True:
        try:
            parts = sub.recv_multipart()
        except zmq.Again:
            continue
        except Exception as exc:
            logger.error(f"[CORE] recv error: {exc}")
            continue

        try:
            # BlueSky sends [topic_bytes, msgpack_bytes]
            if b"ACDATA" not in parts[0]:
                continue

            raw = msgpack.unpackb(parts[1], raw=False)
            if not isinstance(raw, list) or len(raw) < 2:
                continue

            acdata = raw[1]

            # --- یک‌بار کلیدها و مقادیر نمونه را log کن ---
            if not getattr(thread_core_reader, '_keys_logged', False):
                logger.info(f"[CORE] acdata keys: {list(acdata.keys())}")
                for k in list(acdata.keys()):
                    val     = acdata[k]
                    decoded = _decode_numpy(val)
                    if isinstance(decoded, list):
                        sample = [round(v, 4) if isinstance(v, float) else v
                                  for v in decoded[:3]]
                    else:
                        sample = decoded
                    logger.info(f"[CORE]   '{k}': {sample}")
                thread_core_reader._keys_logged = True

            ids   = acdata.get("id",    [])
            types = acdata.get("actype", [])
            lats  = acdata.get("lat",   {})
            lons  = acdata.get("lon",   {})
            alts  = acdata.get("alt",   {})    # metres
            gss   = acdata.get("gs",    {})    # m/s
            tass  = acdata.get("tas",   {})    # m/s — True Air Speed (موجود در این نسخه BS)
            vss   = acdata.get("vs",    {})    # m/s
            # HDG = جهت دماغه، TRK = مسیر واقعی
            # log کلیدهای واقعی را نشان می‌دهد
            _hdg_cands = ["hdg", "heading", "head", "phi"]
            _trk_cands = ["trk", "track", "crs"]
            hdgs = next((acdata[k] for k in _hdg_cands if k in acdata), None)
            trks = next((acdata[k] for k in _trk_cands if k in acdata), None)

            # hdg در acdata این نسخه BS نیست — از plugin (extra_cache) می‌آید
            if hdgs is None:
                hdgs = trks   # fallback تا extra_cache پر شود
            iass  = acdata.get("cas",   acdata.get("ias", acdata.get("CAS", {})))

            aircraft_list = []
            with data_lock:
                for idx, acid_raw in enumerate(ids):
                    acid = acid_raw.decode("utf-8") if isinstance(acid_raw, bytes) else str(acid_raw)
                    ex   = extra_cache.get(acid, {})

                    # --- core fields ---
                    lat_deg  = round(_get_float(lats,  idx), 6)
                    lon_deg  = round(_get_float(lons,  idx), 6)
                    alt_m    = _get_float(alts,  idx)
                    gs_ms_raw = _get_float(gss,   idx)
                    tas_ms    = _get_float(tass,  idx)   # TAS — موجود در acdata
                    vs_ms     = _get_float(vss,   idx)
                    trk_deg = round(_get_float(trks, idx)) if trks is not None else None
                    # hdg از plugin می‌آید (traf.hdg) — اگر نبود از trk
                    _ex_hdg  = ex.get("hdg", None)
                    hdg_deg  = round(float(_ex_hdg)) if _ex_hdg is not None else trk_deg
                    cas_ms    = _get_float(iass,  idx)

                    # unit conversions (1 m/s = 1.94384 kt)
                    MS_TO_KT = 1.94384
                    alt_ft   = round(alt_m    * 3.28084)
                    gs_kt    = round(gs_ms_raw * MS_TO_KT)
                    tas_kt   = round(tas_ms   * MS_TO_KT)
                    vs_fpm   = round(vs_ms    * 196.850)
                    ias_kt   = round(cas_ms   * MS_TO_KT)

                    # Mach از TAS — دقیق‌تر از GS (چون TAS مستقل از باد است)
                    import math as _math
                    if tas_ms > 1.0 and alt_m > 10:
                        T_K  = max(216.65, 288.15 - 0.0065 * min(alt_m, 11000))
                        a_ms = 340.29 * _math.sqrt(T_K / 288.15)
                        mach = round(tas_ms / a_ms, 3)
                    else:
                        mach = 0.0

                    # aircraft type — prefer the richer value from plugin
                    ac_type  = ex.get("actype") or _get_str(types, idx, "UNK")

                    aircraft_list.append({
                        "id"       : acid,
                        "type"     : ac_type,
                        "wtc"      : get_wtc(ac_type),
                        "lat"      : lat_deg,
                        "lon"      : lon_deg,
                        "alt"      : alt_ft,      # feet
                        "gs"       : gs_kt,        # knots
                        "vs"       : vs_fpm,       # ft/min
                        "hdg"      : hdg_deg,      # degrees (None اگر در acdata نبود)
                        "trk"      : trk_deg,      # degrees (None اگر در acdata نبود)
                        "ias"      : ias_kt,        # knots
                        "mach"     : mach,
                        # extra fields from plugin
                        "squawk"   : ex.get("squawk",    "1000"),
                        "situation": ex.get("situation", "NORMAL"),
                        "ident"    : ex.get("ident",     False),
                        "orig"     : ex.get("orig",      ""),
                        "dest"     : ex.get("dest",      ""),
                        "nextwp"   : ex.get("nextwp",    ""),
                        "eta"      : ex.get("eta",       ""),
                        "wpts"     : ex.get("wpts",      []),
                        "cfl"      : ex.get("cfl",       0.0),
                    })

            latest_aircraft = aircraft_list

        except Exception as exc:
            logger.error(f"[CORE] parse error: {exc}")


# ==================================================================
# Build the flat JSON payload sent over WebSocket
# ==================================================================
def build_payload(aircraft: list, sim_time: str) -> str:
    return json.dumps({
        "sim_time" : sim_time,
        "mactid"   : [a["id"]        for a in aircraft],
        "maclat"   : [a["lat"]       for a in aircraft],
        "maclon"   : [a["lon"]       for a in aircraft],
        "macalt"   : [a["alt"]       for a in aircraft],  # feet
        "mactype"  : [a["type"]      for a in aircraft],
        "macwtc"   : [a["wtc"]       for a in aircraft],
        "macgs"    : [a["gs"]        for a in aircraft],  # knots
        "macvs"    : [a["vs"]        for a in aircraft],  # ft/min
        "machdg"   : [a["hdg"]       for a in aircraft],
        "mactrk"   : [a["trk"]       for a in aircraft],
        "macias"   : [a["ias"]       for a in aircraft],  # knots
        "macmach"  : [a["mach"]      for a in aircraft],
        "macsquawk": [a["squawk"]    for a in aircraft],
        "macsit"   : [a["situation"] for a in aircraft],
        "macident" : [a["ident"]     for a in aircraft],
        "macorig"  : [a["orig"]      for a in aircraft],
        "macdest"  : [a["dest"]      for a in aircraft],
        "maceta"   : [a["eta"]       for a in aircraft],
        "macwpts"  : [a["wpts"]      for a in aircraft],
        "macnext"  : [a["nextwp"]    for a in aircraft],
        "maccfl"   : [a["cfl"]       for a in aircraft],
    })


# ==================================================================
# WebSocket handler — pushes latest data to each connected client
# ==================================================================
async def ws_handler(websocket):
    client = websocket.remote_address
    logger.info(f"[WS] Client connected: {client}")
    try:
        while True:
            with data_lock:
                sim_t   = extra_cache.get("sim_time", "00:00:00")
                payload = build_payload(latest_aircraft, sim_t)
            await websocket.send(payload)
            await asyncio.sleep(SEND_INTERVAL)
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"[WS] Client disconnected: {client}")
    except Exception as exc:
        logger.error(f"[WS] handler error: {exc}")


def run_ws_server():
    async def _serve():
        async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
            logger.info(f"[WS] Server listening on ws://{WS_HOST}:{WS_PORT}")
            await asyncio.Future()   # run forever
    asyncio.run(_serve())


# ==================================================================
# Entry point
# ==================================================================
if __name__ == "__main__":
    threading.Thread(target=thread_extras_reader, daemon=True, name="extras-reader").start()
    threading.Thread(target=thread_core_reader,   daemon=True, name="core-reader").start()
    threading.Thread(target=run_ws_server,        daemon=True, name="ws-server").start()
    logger.info("BlueSky Bridge v3.0 started.")
    while True:
        time.sleep(1)
