# -*- coding: utf-8 -*-
"""
PURPOSE: "Who's online" dashboard for Specify 7, built on SpecifyInterface.

Shows one tile per user with activity today (from the spauditlog table),
sorted by most recent activity, plus a status frame for the web asset server.
Runs separately from the home screen:

    pip install flask
    python -m sp7apitoolbox.online_users        (run from the repository root)

Then open http://127.0.0.1:5001

Login is automatic: credentials come from the toolbox config (see
get_credentials() below - this is the one function you may need to adapt).
"""
import threading
import time
from collections import deque
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from flask import Flask, jsonify, render_template_string

# Internal Dependencies
from sp7apitoolbox import configuration, util
from sp7apitoolbox import global_settings as application
from sp7apitoolbox.specify_interface import SpecifyInterface

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
SERVER_TZ = ZoneInfo("Europe/Copenhagen")   # time zone Specify stores timestamps in
DISPLAY_TZ = ZoneInfo("Europe/Copenhagen")  # time zone used for "today" and display
ACTIVE_MINUTES = 10                         # green tile if activity within this many minutes
REFRESH_SECONDS = 10                        # browser polling interval
PORT = 5001
PAGE_SIZE = 500
MAX_PAGES = 20

ASSET_SERVER_URL = application.settings['assetURL']
ASSET_TIMEOUT = 5            # seconds before the asset server counts as down
ASSET_SLOW_MS = 2000         # amber (slow) above this response time
ASSET_HISTORY = 30           # number of recent checks shown as the little bar strip


class LoginError(Exception):
    pass


class LiveStatusDashboard:
    ACTIONS = {0: "Create", 1: "Update", 2: "Delete", 3: "Tree Merge",
              4: "Tree Move", 5: "Tree Synonymize", 6: "Tree Desynonymize"}
    TABLES = {
        1: "CollectionObject", 2: "Locality", 4: "Taxon", 5: "Agent", 7: "Accession", 8: "Address", 9: "Determination", 
        10: "CollectingEvent", 12: "Accession Agent", 17: "Author",
        30: "Collector", 31: "Container", 32: "PaleoContext", 
        41: "Attachment", 42: "AttachmentMetaData", 
        52: "Loan", 53: "Loan Agent", 54: "Loan Preparation", 55: "Loan Return Preparation", 58: "Storage", 
        61: "Other Identifier", 63: "Preparation", 68: "RecordSet", 
        87: "CollectingTrip", 92: "CollectionEventAttribute", 93: "CollectionObjectAttribute",
        100: "Lithostratigraphy", 110: "Collecting Event Attachment", 111: "CollObjAttachment", 
        124: "LocalityDetail", 153: "CollectionObjectProperty",
        500: "PickList", 501: "PickListItem", 504: "SpLocaleContainerItem", 505: "SpLocaleItemString", 
        514: "SpAppResource", 517: "SpQuery", 518: "SpQueryField",
    }

    PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specify - who's online</title>
<style>
  :root { --bg:#f4f5f7; --card:#fff; --text:#1c2430; --muted:#6b7686; --line:#e1e5eb;
          --green:#2e9e5b; --amber:#d99a1e; --grey:#9aa4b2; --err:#c0392b; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#14181d; --card:#1e242c; --text:#e8ecf1; --muted:#97a3b3; --line:#2c343f; }
  }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.4 system-ui,sans-serif; background:var(--bg); color:var(--text); }
  header { display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
           padding:18px 24px; border-bottom:1px solid var(--line); }
  h1 { margin:0; font-size:20px; }
  #status { color:var(--muted); font-size:13px; align-self:center; }
  #banner { display:none; margin:16px 24px 0; padding:12px 16px; border-radius:8px;
            border:1px solid var(--err); color:var(--err); }
  #banner a { color:inherit; font-weight:600; }

  /* Web asset server status frame */
  #assets { margin:16px 24px 0; background:var(--card); border:1px solid var(--line);
            border-radius:8px; padding:12px 16px; display:flex; align-items:center;
            flex-wrap:wrap; gap:8px 24px; }
  #assets .label { font-weight:600; }
  #assets .state { display:flex; align-items:center; gap:8px; }
  #assets .dot { width:12px; height:12px; border-radius:50%; background:var(--grey); flex:none; }
  #assets.up .dot { background:var(--green); }
  #assets.slow .dot { background:var(--amber); }
  #assets.down .dot { background:var(--err); }
  #assets.down .text { color:var(--err); font-weight:600; }
  #assets .detail { color:var(--muted); font-size:13px; }
  #assets a { color:var(--muted); font-size:13px; }
  #strip { display:flex; gap:2px; align-items:flex-end; height:18px; margin-left:auto; }
  #strip span { width:5px; height:100%; border-radius:1px; background:var(--grey); opacity:.9; }
  #strip span.up { background:var(--green); }
  #strip span.slow { background:var(--amber); }
  #strip span.down { background:var(--err); }

  #tiles { padding:24px; display:grid; gap:16px; grid-template-columns:repeat(4, 1fr); }
  @media (max-width:1000px) { #tiles { grid-template-columns:repeat(2, 1fr); } }
  @media (max-width:560px)  { #tiles { grid-template-columns:1fr; } }
  .tile { background:var(--card); border:1px solid var(--line); border-left:6px solid var(--grey);
          border-radius:8px; padding:14px 16px; min-height:110px; }
  .tile.active { border-left-color:var(--green); }
  .tile.recent { border-left-color:var(--amber); }
  .name { font-size:17px; font-weight:600; }
  .action { margin-top:6px; }
  .when { margin-top:8px; font-size:13px; color:var(--muted); }
  .empty { grid-column:1/-1; text-align:center; color:var(--muted); padding:48px 0; }
</style></head>
<body>
<header><h1>Specify - who's online today</h1>
<div id="status">Loading...</div></header>
<div id="banner"></div>

<main id="tiles"></main>

<section id="assets">
  <div class="label">Web asset server</div>
  <div class="state"><span class="dot"></span><span class="text">Checking...</span></div>
  <div class="detail"></div>
  <a href="{{ assets_url }}web_asset_store.xml" target="_blank" rel="noopener">open</a>
  <div id="strip" title="Recent checks, oldest to newest"></div>
</section>

<script>
const REFRESH_MS = {{ refresh }} * 1000;
const SPECIFY_URL = {{ specify_url|tojson }};
const tiles = document.getElementById('tiles');
const statusEl = document.getElementById('status');
const banner = document.getElementById('banner');
const assets = document.getElementById('assets');

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}
function ago(s) {
  if (s < 60) return s + ' s ago';
  if (s < 3600) return Math.floor(s / 60) + ' min ago';
  return Math.floor(s / 3600) + ' h ' + Math.floor((s % 3600) / 60) + ' min ago';
}
function showBanner(kind, detail) {
  banner.replaceChildren();
  if (kind === 'auth') {
    banner.append(document.createTextNode('Could not log in to Specify with the configured credentials. '));
    const a = el('a', null, 'Open Specify in a new tab');
    a.href = SPECIFY_URL; a.target = '_blank'; a.rel = 'noopener';
    banner.append(a, document.createTextNode(' to check the account, fix the config, and restart this app. Retrying automatically.'));
  } else {
    banner.textContent = 'Could not fetch data: ' + detail;
  }
  banner.style.display = 'block';
}
function render(users) {
  tiles.replaceChildren();
  if (!users.length) { tiles.append(el('div', 'empty', 'No activity today yet.')); return; }
  for (const u of users) {
    const t = el('div', 'tile ' + (u.active ? 'active' : (u.seconds_ago <= 4800 ? 'recent' : '')));
    t.append(el('div', 'name', u.name));
    const a = el('div', 'action');
    a.append(el('b', null, u.action), document.createTextNode(' on ' + u.table));
    t.append(a, el('div', 'when', ago(u.seconds_ago) + ' (' + u.time + ')'));
    tiles.append(t);
  }
}
async function refresh() {
  try {
    const data = await (await fetch('/api/online', { cache: 'no-store' })).json();
    if (!data.ok) { showBanner(data.error, data.detail); statusEl.textContent = 'Update failed'; return; }
    banner.style.display = 'none';
    render(data.users);
    statusEl.textContent = data.users.length + ' user(s) today - updated ' + new Date().toLocaleTimeString();
  } catch (e) { showBanner('other', e.message); }
}

function renderAssets(d) {
  assets.className = d.state;
  assets.querySelector('.text').textContent =
    d.state === 'down' ? 'Down' : (d.state === 'slow' ? 'Slow' : 'Online');
  const bits = [];
  if (d.status_code) bits.push('HTTP ' + d.status_code);
  if (d.ms != null) bits.push(d.ms + ' ms');
  if (d.error) bits.push(d.error);
  bits.push('checked ' + d.time);
  assets.querySelector('.detail').textContent = bits.join(' - ');
  const strip = document.getElementById('strip');
  strip.replaceChildren();
  for (const h of d.history) strip.append(el('span', h));
}
async function refreshAssets() {
  try {
    renderAssets(await (await fetch('/api/assets', { cache: 'no-store' })).json());
  } catch (e) {
    assets.className = 'down';
    assets.querySelector('.text').textContent = 'Status unavailable';
    assets.querySelector('.detail').textContent = 'Dashboard backend not reachable';
  }
}

refresh(); refreshAssets();
setInterval(refresh, REFRESH_MS);
setInterval(refreshAssets, REFRESH_MS);
</script></body></html>
"""

    def __init__(self):
        self.agent_names = {}
        self._cache = {"t": 0.0, "payload": None}
        self._lock = threading.Lock()
        # The asset server check has its own cache and lock so that a slow or hanging
        # asset server can never delay the user tiles (and vice versa).
        self._asset_cache = {"t": 0.0, "payload": None}
        self._asset_lock = threading.Lock()
        self._asset_history = deque(maxlen=ASSET_HISTORY)
        self.app = Flask(__name__)
        self.app.add_url_rule("/api/online", "online", self.online)
        self.app.add_url_rule("/api/assets", "assets", self.assets)
        self.app.add_url_rule("/", "index", self.index)

        args = util.parseCommandLineArgs()
        site = args.site
        self.cfg = configuration.ConfigurationHandler()
        self.cfg.loadConfiguration(site)

    @staticmethod
    def get_credentials():
        """
        ADAPT THIS to your config file's key names.
        Returns (username, password, collection_id) for the Specify service account.
        """
        s = application.settings
        return s['username'], s['password'], s['collectionId']

    def ensure_login(self, force=False):
        """Make sure the session is valid; (re)log in with the configured credentials if not."""
        if not force and self.cfg.sp.csrfToken and self.cfg.sp.verifySession(self.cfg.sp.csrfToken):
            return
        username, password, collection_id = self.get_credentials()
        if not self.cfg.sp.specifyLogin(username, password, collection_id):
            raise LoginError("Automatic login to Specify failed")

    def agent_id_from(self, value):
        """createdbyagent may be '/api/specify/agent/42/', 42, or a nested object."""
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get("id") or value.get("resource_uri")
        if isinstance(value, int):
            return value
        tail = str(value).rstrip("/").rsplit("/", 1)[-1]
        return int(tail) if tail.isdigit() else None

    def agent_name(self, agent_id):
        if agent_id not in self.agent_names:
            a = self.cfg.sp.getSpecifyObject("agent", agent_id) or {}
            parts = [a.get("firstname"), a.get("lastname")]
            self.agent_names[agent_id] = " ".join(p for p in parts if p) or f"Agent {agent_id}"
        return self.agent_names[agent_id]

    def parse_ts(self, value):
        s = str(value).replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            dt = datetime.fromisoformat(s[:19])   # drop odd fractional seconds
        return dt if dt.tzinfo else dt.replace(tzinfo=SERVER_TZ)

    def fetch_audit_rows(self, since):
        """All audit log rows since the cutoff, newest first. getSpecifyObjects returns {} on error."""
        rows = []
        for page in range(MAX_PAGES):
            batch = self.cfg.sp.getSpecifyObjects(
                "spauditlog",
                limit=PAGE_SIZE,
                offset=page * PAGE_SIZE,
                filters={"timestampcreated__gt": since},
                sort="-timestampcreated",
            )
            if not isinstance(batch, list):
                return None
            rows.extend(batch)
            if len(batch) < PAGE_SIZE:
                break
        return rows

    def fetch_users(self):
        self.ensure_login()

        now = datetime.now(DISPLAY_TZ)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        since = midnight.astimezone(SERVER_TZ).strftime("%Y-%m-%dT%H:%M:%S")

        rows = self.fetch_audit_rows(since)
        if rows is None:
            self.ensure_login(force=True)
            rows = self.fetch_audit_rows(since)
            if rows is None:
                raise RuntimeError(
                    "Specify returned an error for the audit log query "
                    "(see log; the service account may lack permission)"
                )

        latest = {}
        for row in rows:
            aid = self.agent_id_from(row.get("createdbyagent"))
            if aid is not None and aid not in latest:
                latest[aid] = row

        users = []
        for aid, row in latest.items():
            ts = self.parse_ts(row["timestampcreated"])
            secs = max(0, int((now - ts).total_seconds()))
            users.append({
                "name": self.agent_name(aid),
                "action": self.ACTIONS.get(row.get("action"), "Unknown"),
                "table": self.TABLES.get(row.get("tablenum"), f"Table {row.get('tablenum')}"),
                "seconds_ago": secs,
                "time": ts.astimezone(DISPLAY_TZ).strftime("%H:%M:%S"),
                "active": secs <= ACTIVE_MINUTES * 60,
            })
        users.sort(key=lambda u: u["seconds_ago"])
        return users

    def check_asset_server(self):
        """Ping the web asset server once. Returns a result dict; never raises."""
        started = time.perf_counter()
        status_code, error = None, None
        try:
            r = requests.get(ASSET_SERVER_URL, timeout=ASSET_TIMEOUT)
            status_code = r.status_code
            if r.status_code >= 400:
                error = r.reason or "error response"
            elif not r.content:
                error = "empty response"
        except requests.exceptions.Timeout:
            error = f"no response within {ASSET_TIMEOUT} s"
        except requests.exceptions.SSLError:
            error = "SSL error"
        except requests.exceptions.ConnectionError:
            error = "connection failed"
        except Exception as e:
            error = str(e)
        ms = int((time.perf_counter() - started) * 1000)

        if error:
            state = "down"
        elif ms > ASSET_SLOW_MS:
            state = "slow"
        else:
            state = "up"

        self._asset_history.append(state)
        return {
            "state": state,
            "status_code": status_code,
            "ms": ms if status_code else None,
            "error": error,
            "time": datetime.now(DISPLAY_TZ).strftime("%H:%M:%S"),
            "history": list(self._asset_history),
        }

    def assets(self):
        with self._asset_lock:
            if self._asset_cache["payload"] is None or \
                    time.time() - self._asset_cache["t"] > REFRESH_SECONDS - 1:
                self._asset_cache["payload"] = self.check_asset_server()
                self._asset_cache["t"] = time.time()
            return jsonify(self._asset_cache["payload"])

    def online(self):
        with self._lock:
            if self._cache["payload"] is None or time.time() - self._cache["t"] > REFRESH_SECONDS - 1:
                try:
                    self._cache["payload"] = {"ok": True, "users": self.fetch_users()}
                except LoginError as e:
                    util.logger.error(str(e))
                    self._cache["payload"] = {"ok": False, "error": "auth", "detail": str(e)}
                except Exception as e:
                    util.logger.error(f"Online users fetch failed: {e}")
                    self._cache["payload"] = {"ok": False, "error": "other", "detail": str(e)}
                self._cache["t"] = time.time()
            return jsonify(self._cache["payload"])

    def index(self):
        return render_template_string(self.PAGE, refresh=REFRESH_SECONDS,
                                      specify_url=application.settings['baseURL'],
                                      assets_url=application.settings['assetURL'])

    def run(self):
        # threaded so the slower asset check never blocks the user tiles request
        self.app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)


dashboard = LiveStatusDashboard()
app = dashboard.app


def main():
    dashboard.run()


if __name__ == "__main__":
    main()