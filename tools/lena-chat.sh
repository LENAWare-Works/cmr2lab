#!/usr/bin/env bash
# lena-chat.sh — direct channel between an AI agent and Lena.
# No account, no token, no port, no firewall. Both sides dial OUT to a public relay.
#
#   ./lena-chat.sh read          # messages waiting for you
#   ./lena-chat.sh write "text"  # send Lena a message
#   ./lena-chat.sh whoami        # show channel state
#
set -u
SERVER="https://ntfy.sh"
INBOX="lena2dc-mitn3jhq0xs0yb1q9t7ayfmbqz4u"    # Lena -> you
OUTBOX="dc2lena-2mnql963ughdypjw6f09lf4l9jq7"   # you -> Lena
STATE="${LENA_CHAT_STATE:-$HOME/.lena-chat-last}"

case "${1:-}" in
  read)
    since=0; [ -f "$STATE" ] && since=$(cat "$STATE" 2>/dev/null || echo 0)
    [ "$since" -gt 5 ] && since=$((since-5))   # 5s overlap; duplicates beat missing
    out=$(curl -s -m 20 "$SERVER/$INBOX/json?poll=1&since=$since" 2>/dev/null)
    now=$(date +%s); echo "$now" > "$STATE"
    if [ -z "$out" ]; then
      echo "(nothing new from Lena)"
    else
      echo "$out" | grep '"event":"message"' || echo "(nothing new from Lena)"
    fi
    ;;
  write)
    [ $# -ge 2 ] || { echo 'usage: lena-chat.sh write "your message"'; exit 1; }
    shift
    msg="$*"
    printf '%s' "$msg" | curl -s -m 20 --data-binary @- \
      -H "Title: DeepCode" -H "Tags: robot" "$SERVER/$OUTBOX" -o /dev/null -w "sent (%{http_code})\n"
    ;;
  whoami)
    echo "server : $SERVER"
    echo "inbox  : $INBOX   (Lena -> you)"
    echo "outbox : $OUTBOX  (you -> Lena)"
    echo "state  : $STATE"
    ;;
  *)
    echo "usage: $0 read | write \"message\" | whoami"
    ;;
esac
