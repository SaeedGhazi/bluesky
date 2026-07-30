import numpy as np
import zmq
import json
import logging
from bluesky import core, stack, traf, sim

# ================================================================
#  ATC EXTRAS Plugin — Version 2.3
#  ZMQ PUB port 11005
# ================================================================

logger = logging.getLogger("ATC_EXTRAS")


class ATCExtras(core.Entity):
    def __init__(self):
        super().__init__()
        self.context = zmq.Context()
        self.socket  = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:11005")

        with self.settrafarrays():
            self.squawk     = np.array([], dtype=object)
            self.situation  = np.array([], dtype=object)
            self.ident      = np.array([], dtype=bool)
            self.ident_time = np.array([], dtype=float)
            self.cfl        = np.array([], dtype=float)
            self.hdg        = np.array([], dtype=float)  # heading — از traf.hdg

    def create(self, n=1):
        super().create(n)
        self.squawk[-n:]     = ["1000"]   * n
        self.situation[-n:]  = ["NORMAL"] * n
        self.ident[-n:]      = [False]    * n
        self.ident_time[-n:] = [0.0]     * n
        self.cfl[-n:]        = [0.0]     * n
        self.hdg[-n:]        = [0.0]     * n

    @stack.command(name='SQWK')
    def sqwk(self, idx: 'acid', code):
        str_code = str(code)
        if isinstance(idx, list):
            for i in idx: self.squawk[i] = str_code
        else: self.squawk[idx] = str_code
        return True, f"Squawk updated to {str_code}"

    @stack.command(name='SITSIT')
    def sitsit(self, idx: 'acid', situation: str):
        sit = situation.upper()
        if isinstance(idx, list):
            for i in idx: self.situation[i] = sit
        else: self.situation[idx] = sit
        return True, f"Situation set to {sit}"

    @stack.command(name='CFL')
    def set_cfl(self, idx: 'acid', level: float):
        """Set Cleared Flight Level. Use feet: CFL AAA 35000 or FL: CFL AAA 350"""
        # اگر مقدار کوچک‌تر از ۱۰۰۰ باشد FL است، وگرنه feet
        ft = level * 100 if level < 1000 else level
        if isinstance(idx, list):
            for i in idx: self.cfl[i] = ft
        else: self.cfl[idx] = ft
        return True, f"CFL set to {formatLevel(ft) if False else int(ft)}ft"

    @stack.command(name='IDENT')
    def set_ident(self, idx: 'acid'):
        t = sim.simt
        if isinstance(idx, list):
            for i in idx:
                self.ident[i]      = True
                self.ident_time[i] = t
        else:
            self.ident[idx]      = True
            self.ident_time[idx] = t
        return True, "IDENT activated (auto-cancel in 20s)"

    # ------------------------------------------------------------------
    # RTEDEBUG — نشان دادن تمام attributes موجود در Route object
    # ------------------------------------------------------------------
    @stack.command(name='RTEDEBUG')
    def rtedebug(self, idx: 'acid'):
        i = idx if not isinstance(idx, list) else idx[0]
        acid = traf.id[i]
        lines = [f"=== RTEDEBUG {acid} ==="]
        try:
            rt = traf.ap.route[i]
            # تمام attributes غیر-private
            attrs = [a for a in dir(rt) if not a.startswith('_')]
            lines.append(f"dir(rt): {attrs}")
            lines.append(f"iactwp : {rt.iactwp}")
            lines.append(f"wpname : {list(rt.wpname)}")
            # بررسی نام های مختلف ممکن برای좌표
            for cand in ['wplat','wplon','wplatlon','lat','lon','wplatlons',
                         'wplatvec','wplonvec','aclat','aclon']:
                if hasattr(rt, cand):
                    val = getattr(rt, cand)
                    try:
                        lines.append(f"rt.{cand} : {list(val)[:6]}")
                    except Exception:
                        lines.append(f"rt.{cand} : {val}")
            lines.append(f"ac pos : lat={traf.lat[i]:.4f} lon={traf.lon[i]:.4f}")
            lines.append(f"gs(kt) : {traf.gs[i]:.1f}")
            # test navdb lookup
            try:
                from bluesky import navdb
                for wn in list(rt.wpname)[:3]:
                    r = navdb.getwpt(str(wn))
                    lines.append(f"navdb[{wn}]: {r[0] if r else 'NOT FOUND'}")
            except Exception as e:
                lines.append(f"navdb error: {e}")
            try:
                utc = sim.utc
                lines.append(f"utc    : {utc.hour:02d}:{utc.minute:02d}:{utc.second:02d}")
            except Exception as e:
                lines.append(f"utc err: {e}")
        except Exception as e:
            lines.append(f"ERROR: {e}")
        msg = "\n".join(lines)
        logger.warning("\n" + msg)
        return True, msg

    # ------------------------------------------------------------------
    def _dist_nm(self, lat1, lon1, lat2, lon2):
        dlat = (float(lat1) - float(lat2)) * 60.0
        dlon = (float(lon1) - float(lon2)) * 60.0 * np.cos(
            np.radians((float(lat1) + float(lat2)) / 2.0))
        return float(np.sqrt(dlat**2 + dlon**2))

    def _sec_to_hhmm(self, total_sec):
        s = total_sec % 86400
        return f"{int(s // 3600):02d}:{int((s % 3600) // 60):02d}:{int(s % 60):02d}"

    def _get_wplat(self, rt):
        """مختصات lat waypoint ها را از Route یا navdb می‌خواند."""
        # روش ۱: attribute مستقیم روی route
        for name in ('wplat', 'lat', 'wplatvec', 'aclat'):
            if hasattr(rt, name):
                try:
                    return [float(v) for v in getattr(rt, name)]
                except Exception:
                    pass
        # روش ۲: wplatlon (برخی نسخه‌های BS)
        if hasattr(rt, 'wplatlon'):
            try:
                return [float(v[0]) for v in rt.wplatlon]
            except Exception:
                pass
        # روش ۳: navdb lookup
        return self._lookup_wplat(rt)

    def _get_wplon(self, rt):
        for name in ('wplon', 'lon', 'wplonvec', 'aclon'):
            if hasattr(rt, name):
                try:
                    return [float(v) for v in getattr(rt, name)]
                except Exception:
                    pass
        if hasattr(rt, 'wplatlon'):
            try:
                return [float(v[1]) for v in rt.wplatlon]
            except Exception:
                pass
        return self._lookup_wplon(rt)

    def _lookup_wplat(self, rt):
        """lookup lat از navdb بر اساس wpname."""
        try:
            from bluesky import navdb
            lats = []
            for name in rt.wpname:
                results = navdb.getwpt(str(name))
                if results and len(results) > 0:
                    lats.append(float(results[0][1]))  # lat
                else:
                    return None  # یک نام پیدا نشد → کل مسیر نامعتبر
            return lats if lats else None
        except Exception:
            return None

    def _lookup_wplon(self, rt):
        """lookup lon از navdb بر اساس wpname."""
        try:
            from bluesky import navdb
            lons = []
            for name in rt.wpname:
                results = navdb.getwpt(str(name))
                if results and len(results) > 0:
                    lons.append(float(results[0][2]))  # lon
                else:
                    return None
            return lons if lons else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    @core.timed_function(name='atc_telemetry', dt=1.0)
    def update(self):
        sim_t = sim.simt

        try:
            utc = sim.utc
            utc_sod = utc.hour * 3600 + utc.minute * 60 + utc.second
        except Exception:
            utc_sod = sim_t % 86400

        payload = {"sim_time": self._sec_to_hhmm(utc_sod)}

        # auto-cancel IDENT after 20 seconds
        for i in range(len(traf.id)):
            if self.ident[i] and (sim_t - self.ident_time[i]) >= 20.0:
                self.ident[i] = False

        for i, acid in enumerate(traf.id):
            gs_ms      = float(traf.gs[i]) * 0.514444
            # heading از traf.hdg — این مستقل از باد است (جهت دماغه)
            try:
                self.hdg[i] = float(traf.hdg[i])
            except Exception:
                pass
            nextwp_val = ""
            eta_val    = ""
            wpts_val   = []

            rt = None
            try:
                rt = traf.ap.route[i]
            except Exception:
                pass

            if rt is not None and gs_ms > 0.5:
                try:
                    iactwp  = int(rt.iactwp)
                    wpnames = [str(n) for n in rt.wpname]
                    wplats  = self._get_wplat(rt)
                    wplons  = self._get_wplon(rt)
                    n_wpts  = len(wpnames)

                    if iactwp < 0:
                        iactwp = 0

                    if wplats is None or wplons is None:
                        #좌표 در دسترس نیست — فقط nextwp را نشان بده
                        if n_wpts > 0 and iactwp < n_wpts:
                            nextwp_val = wpnames[iactwp]
                    elif n_wpts > 0 and iactwp < n_wpts:
                        nextwp_val = wpnames[iactwp]
                        cum_sec    = 0.0

                        for j in range(iactwp, n_wpts):
                            lat_s = traf.lat[i] if j == iactwp else wplats[j - 1]
                            lon_s = traf.lon[i] if j == iactwp else wplons[j - 1]
                            lat_e = wplats[j]
                            lon_e = wplons[j]

                            dist_nm  = self._dist_nm(lat_s, lon_s, lat_e, lon_e)
                            cum_sec += (dist_nm * 1852.0) / gs_ms

                            est_sod = utc_sod + cum_sec
                            wpts_val.append({
                                "name": wpnames[j],
                                "est" : self._sec_to_hhmm(est_sod)
                            })

                        if wpts_val:
                            eta_val = wpts_val[-1]["est"]

                except Exception as e:
                    logger.debug(f"[{acid}] route error: {e}")

            orig_val = dest_val = ""
            try:
                if hasattr(traf.ap, 'orig') and i < len(traf.ap.orig):
                    orig_val = str(traf.ap.orig[i])
                if hasattr(traf.ap, 'dest') and i < len(traf.ap.dest):
                    dest_val = str(traf.ap.dest[i])
            except Exception:
                pass

            # CFL: اگر با CFL command set شده از آن استفاده کن
            # در غیر این صورت از traf.ap.alt (ارتفاع هدف = ALT command) بخوان
            cfl_val = float(self.cfl[i])
            if cfl_val == 0.0:
                try:
                    ap_alt_m = float(traf.ap.alt[i])
                    if ap_alt_m > 10:
                        cfl_val = round(ap_alt_m * 3.28084)
                except Exception:
                    pass

            payload[acid] = {
                "actype"   : str(traf.type[i]),
                "squawk"   : str(self.squawk[i]),
                "situation": str(self.situation[i]),
                "ident"    : bool(self.ident[i]),
                "cfl"      : cfl_val,
                "orig"     : orig_val,
                "dest"     : dest_val,
                "nextwp"   : nextwp_val,
                "eta"      : eta_val,
                "wpts"     : wpts_val,
                "hdg"      : round(float(self.hdg[i]), 1),
            }

        self.socket.send_string(f"EXTRADATA {json.dumps(payload)}")


def init_plugin():
    return {
        'plugin_name': 'ATC_EXTRAS',
        'plugin_type': 'sim',
        'entity'     : ATCExtras(),
    }
