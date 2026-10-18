#!/usr/bin/env python3
# lena-bridge.py — cross-platform bridge. Runs on Linux, WSL, Windows, macOS.
# Put it wherever DeepCode's CLI lives. After that, the two agents talk directly.
#
#   Linux / SteamOS / WSL :  DC_CMD=deepcode python3 lena-bridge.py
#   Windows (cmd)         :  set DC_CMD=deepcode && python lena-bridge.py
#   Windows (PowerShell)  :  $env:DC_CMD="deepcode"; python lena-bridge.py
#
# DC_CMD = how you invoke DeepCode so that it reads a prompt on stdin and prints a reply.
# DC_ARGS = extra flags, space separated (optional).

import os, sys, json, time, subprocess, urllib.request, pathlib

SERVER = "https://ntfy.sh"
INBOX  = "lena2dc-mitn3jhq0xs0yb1q9t7ayfmbqz4u"
OUTBOX = "dc2lena-2mnql963ughdypjw6f09lf4l9jq7"
POLL   = int(os.environ.get("POLL_SECS", "20"))
STATE  = pathlib.Path(os.environ.get("BRIDGE_STATE", pathlib.Path.home() / ".lena-bridge-last"))
SEEN   = pathlib.Path(os.environ.get("BRIDGE_SEEN",  pathlib.Path.home() / ".lena-bridge-seen"))
LOG    = pathlib.Path(os.environ.get("BRIDGE_LOG",   pathlib.Path.home() / ".lena-bridge.log"))

DC_CMD  = os.environ.get("DC_CMD", "").strip()
DC_ARGS = os.environ.get("DC_ARGS", "").split()

def log(s):
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {s}\n")
    except Exception:
        pass

def fetch(since):
    url = f"{SERVER}/{INBOX}/json?poll=1&since={since}"
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        log(f"fetch error: {e}")
        return ""

def publish(text):
    try:
        req = urllib.request.Request(
            f"{SERVER}/{OUTBOX}", data=text.encode("utf-8"), method="POST",
            headers={"Title": "DeepCode", "Tags": "robot"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except Exception as e:
        log(f"publish error: {e}")
        return 0

def load_seen():
    try:
        return set(SEEN.read_text().split())
    except Exception:
        return set()

def save_seen(ids):
    try:
        SEEN.write_text("\n".join(list(ids)[-400:]))
    except Exception:
        pass

def main():
    if not DC_CMD:
        print("ERROR: set DC_CMD to how you invoke DeepCode (must read stdin, print reply).")
        print("  Linux  : DC_CMD=deepcode python3 lena-bridge.py")
        print('  Windows: set DC_CMD=deepcode && python lena-bridge.py')
        sys.exit(1)

    print(f"bridge up — DC_CMD={DC_CMD} {DC_ARGS} — polling every {POLL}s. Ctrl-C to stop.")
    log(f"=== bridge start (python): {DC_CMD} {DC_ARGS} ===")

    while True:
        try:
            since = 0
            try:
                since = int(STATE.read_text().strip())
            except Exception:
                pass
            if since > 5:
                since -= 5
            raw = fetch(since)
            try:
                STATE.write_text(str(int(time.time())))
            except Exception:
                pass

            seen = load_seen()
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("event") != "message":
                    continue
                mid = d.get("id", "")
                if mid and mid in seen:
                    continue          # already handled; the overlap window re-serves it
                msg = d.get("message", "").strip()
                if not msg:
                    continue
                if mid:
                    seen.add(mid)
                    save_seen(seen)

                log("IN: " + msg[:120])
                print(f"\n<< {msg[:300]}")
                try:
                    p = subprocess.run([DC_CMD] + DC_ARGS, input=msg,
                                       capture_output=True, text=True, timeout=600)
                    reply = (p.stdout or "").strip() or (p.stderr or "").strip()
                except subprocess.TimeoutExpired:
                    reply = "(DeepCode timed out after 600s)"
                except FileNotFoundError:
                    reply = f"(DC_CMD '{DC_CMD}' not found on this machine)"
                except Exception as e:
                    reply = f"(bridge error running DeepCode: {e})"

                if not reply:
                    reply = "(DeepCode returned nothing)"
                reply = reply[-3500:]
                log("OUT: " + reply[:120])
                print(f">> {reply[:300]}")
                code = publish(reply)
                print(f"   relayed ({code})")
        except KeyboardInterrupt:
            print("\nstopped.")
            return
        except Exception as e:
            log(f"loop error: {e}")
        time.sleep(POLL)

if __name__ == "__main__":
    main()
