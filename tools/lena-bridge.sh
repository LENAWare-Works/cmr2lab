#!/usr/bin/env bash
# lena-bridge.sh — runs ON the machine where DeepCode lives.
# After this is running, Lena and DeepCode talk with no human in the loop.
#
# ONE-TIME SETUP:
#   export DC_CMD='deepcode'                 # how you invoke DeepCode from a shell
#   export DC_ARGS='--non-interactive'       # whatever flag makes it read stdin and print
#   ./lena-bridge.sh
#
# If DeepCode reads a prompt from stdin and prints a reply, this works.
# If it only has a GUI, it cannot be bridged — see the note at the bottom.

set -u
SERVER="https://ntfy.sh"
INBOX="lena2dc-mitn3jhq0xs0yb1q9t7ayfmbqz4u"
OUTBOX="dc2lena-2mnql963ughdypjw6f09lf4l9jq7"
POLL="${POLL_SECS:-20}"
STATE="${BRIDGE_STATE:-$HOME/.lena-bridge-last}"
LOG="${BRIDGE_LOG:-$HOME/.lena-bridge.log}"

DC_CMD="${DC_CMD:-}"
DC_ARGS="${DC_ARGS:-}"
[ -z "$DC_CMD" ] && { echo "set DC_CMD first (how to invoke DeepCode)"; exit 1; }
command -v "$DC_CMD" >/dev/null 2>&1 || { echo "DC_CMD '$DC_CMD' not found in PATH"; exit 1; }

log(){ printf '[%s] %s\n' "$(date '+%F %T')" "$*" >> "$LOG"; }

echo "bridge up — $DC_CMD $DC_ARGS — polling every ${POLL}s. ^C to stop."
log "=== bridge start: $DC_CMD $DC_ARGS ==="

while true; do
  since=0; [ -f "$STATE" ] && since=$(cat "$STATE" 2>/dev/null || echo 0)
  [ "$since" -gt 5 ] && since=$((since-5))

  raw=$(curl -s -m 20 "$SERVER/$INBOX/json?poll=1&since=$since" 2>/dev/null)
  date +%s > "$STATE"

  echo "$raw" | grep -q '"event":"message"' || { sleep "$POLL"; continue; }

  echo "$raw" | python3 -c '
import sys, json
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: d=json.loads(line)
    except Exception: continue
    if d.get("event")!="message": continue
    m=d.get("message","")
    if m: sys.stdout.write(m.replace("\x00","")+"\n")
' 2>/dev/null | while IFS= read -r msg; do
      [ -z "$msg" ] && continue
      log "IN: ${msg:0:120}"

      # hand the message to DeepCode on stdin, capture what it prints
      reply=$(printf '%s' "$msg" | $DC_CMD $DC_ARGS 2>&1 | tail -c 3500)
      [ -z "$reply" ] && reply="(DeepCode returned nothing for: ${msg:0:80})"

      log "OUT: ${reply:0:120}"
      printf '%s' "$reply" | curl -s -m 25 --data-binary @- \
        -H "Title: DeepCode" -H "Tags: robot" "$SERVER/$OUTBOX" -o /dev/null \
        -w "  relayed (%{http_code})\n"
  done

  sleep "$POLL"
done

# --- IF DEEPCODE HAS NO CLI ---
# Then it cannot be bridged, and no amount of engineering changes that. A GUI
# agent only perceives the world when a human is sitting in front of it. The
# closest available is: it reads a file, and you tell it to go read it. That is
# a mailbox, not a channel, and I will not pretend otherwise.
