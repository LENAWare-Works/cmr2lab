#!/usr/bin/env python3
# lena-bridge.py — headless bridge between Lena and DeepCode.
#
# Works with a CLI that takes the prompt as an ARGUMENT (deepcode exec "..."),
# or one that reads stdin. Put {prompt} in DC_ARGS to mark the argument slot.
#
#   Windows  :  $env:DC_CMD="deepcode"; $env:DC_ARGS='exec {prompt} --json'
#   Linux    :  DC_CMD=deepcode DC_ARGS='exec {prompt} --json' python3 lena-bridge.py
#
# Topics are NOT in this file. Generate them once and keep them private:
#   python lena-bridge.py --newtopic
#
# Test the CLI without touching the network:
#   python lena-bridge.py --test "say hello"

import os, sys, json, time, re, subprocess, urllib.request, urllib.error, pathlib, secrets

SERVER = os.environ.get("BRIDGE_SERVER", "https://ntfy.sh").rstrip("/")
INBOX  = os.environ.get("BRIDGE_IN", "").strip()
OUTBOX = os.environ.get("BRIDGE_OUT", "").strip()
POLL   = int(os.environ.get("POLL_SECS", "20"))
TIMEOUT= int(os.environ.get("DC_TIMEOUT", "900"))

HOME   = pathlib.Path.home()
SEEN   = pathlib.Path(os.environ.get("BRIDGE_SEEN", HOME / ".lena-bridge-seen"))
LOG    = pathlib.Path(os.environ.get("BRIDGE_LOG",  HOME / ".lena-bridge.log"))
CMDF   = pathlib.Path(os.environ.get("BRIDGE_CMDFILE", HOME / ".lena-bridge-cmd"))

DC_CMD  = os.environ.get("DC_CMD", "").strip()
DC_ARGS = os.environ.get("DC_ARGS", "").strip()

def log(s):
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {s}\n")
    except Exception:
        pass

def seen_load():
    try: return set(SEEN.read_text().split())
    except Exception: return set()

def seen_add(mid):
    try:
        with SEEN.open("a") as f: f.write(mid + "\n")
    except Exception: pass

# ---------- running DeepCode ----------

def run_dc(prompt):
    """Run DeepCode with the prompt. Returns (ok, text)."""
    cmd = DC_CMD or "deepcode"

    if "{prompt}" in DC_ARGS:
        args = [a.replace("{prompt}", prompt) for a in shlex_split(DC_ARGS)]
        argv = [cmd] + args
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT)
        except FileNotFoundError:
            return False, f"command not found: {cmd}"
        except subprocess.TimeoutExpired:
            return False, f"timed out after {TIMEOUT}s"
        out = (p.stdout or "") + (("\n" + p.stderr) if p.returncode and p.stderr else "")
        return p.returncode == 0, out.strip()

    # fallback: stdin
    argv = [cmd] + shlex_split(DC_ARGS)
    try:
        p = subprocess.run(argv, input=prompt, capture_output=True, text=True, timeout=TIMEOUT)
    except FileNotFoundError:
        return False, f"command not found: {cmd}"
    except subprocess.TimeoutExpired:
        return False, f"timed out after {TIMEOUT}s"
    out = (p.stdout or "") + (("\n" + p.stderr) if p.returncode and p.stderr else "")
    return p.returncode == 0, out.strip()

def shlex_split(s):
    import shlex
    return shlex.split(s, posix=(os.name != "nt"))

# ---------- ntfy ----------

def post(topic, body, title=None):
    data = body.encode("utf-8")
    req = urllib.request.Request(f"{SERVER}/{topic}", data=data, method="POST")
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    if title: req.add_header("Title", title.encode("ascii", "replace").decode())
    req.add_header("Priority", "default")
    req.add_header("Tags", "speech_balloon")
    try:
        urllib.request.urlopen(req, timeout=20)
        return True
    except Exception as e:
        log(f"post error: {e}")
        return False

def fetch(since):
    url = f"{SERVER}/{INBOX}/json?poll=1&since={since}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        log(f"fetch error: {e}")
        return ""

def messages(raw):
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if not line: continue
        try: d = json.loads(line)
        except Exception: continue
        if d.get("event") != "message": continue
        msg = d.get("message") or ""
        if not msg.strip(): continue
        out.append((d.get("id") or "", d.get("time") or 0, msg))
    return out

# ---------- main ----------

def main():
    if "--newtopic" in sys.argv:
        print(f"BRIDGE_IN={secrets.token_hex(16)}")
        print(f"BRIDGE_OUT={secrets.token_hex(16)}")
        return

    if "--test" in sys.argv:
        i = sys.argv.index("--test")
        prompt = " ".join(sys.argv[i+1:]) or "say hello and stop"
        ok, txt = run_dc(prompt)
        print(f"cmd: {DC_CMD or 'deepcode'}   args: {DC_ARGS or '(stdin)'}")
        print(f"exit ok: {ok}")
        print("--- output ---")
        print(txt if txt else "(empty)")
        return

    if not INBOX or not OUTBOX:
        print("No topics set. Run: python lena-bridge.py --newtopic")
        print("then export BRIDGE_IN and BRIDGE_OUT.")
        sys.exit(1)

    print(f"bridge up. in={INBOX[:6]}… out={OUTBOX[:6]}… poll={POLL}s")
    print(f"deepcode: {DC_CMD or 'deepcode'} {DC_ARGS}")
    print("ctrl-c to stop\n")

    seen = seen_load()
    since = "all"

    while True:
        raw = fetch(since)
        if raw:
            msgs = messages(raw)
            if msgs:
                since = str(max(m[1] for m in msgs))
                for mid, ts, body in msgs:
                    if mid in seen:
                        continue
                    seen.add(mid); seen_add(mid)
                    print(f"[in] {body[:80]}")
                    ok, txt = run_dc(body)
                    if not txt:
                        txt = "(no output)"
                    if not ok:
                        txt = f"FAILED\n{txt}"
                    post(OUTBOX, txt, title="lena-bridge")
                    print(f"[out] {'ok' if ok else 'FAILED'} {len(txt)} chars")
        time.sleep(POLL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped.")
