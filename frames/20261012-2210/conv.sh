set -e
cd /home/deck/lena/work
OUT=/home/deck/lena/work/FRAMES-PUB-20261012-2210/raw
mkdir -p "$OUT"
conv() {
  python3 /home/deck/lena/work/RACE/ppm2png.py "$1" "$OUT/$2" >/dev/null && echo "OK $2 $(stat -c%s "$OUT/$2")"
}
conv FIXIT-20261012-2158/shots/CAND.ppm.3000      A-cur-f3000.png
conv FIXIT-20261012-2158/shots/CAND.ppm.4000      A-cur-f4000.png
conv FIXIT-20261012-2158/shots/CAND.ppm.5000      A-cur-f5000.png
conv FIXBOTH-20261012/shots/fx-b.ppm.2600         B-0927-f2600.png
conv FIXBOTH-20261012/shots/fx-b.ppm.4000         B-0927-f4000.png
conv FIXBOTH-20261012/shots/fx-b.ppm.5000         B-0927-f5000.png
conv FIXBOTH-20261012/shots/fx-b.ppm.5500         B-0927-f5500.png
conv CAR-r38/shots/r38_menu.ppm.000               MENU-1051-f000.png
conv PLAYABLE-20261012/shots/v2.ppm.3000          B-0927-v2-f3000.png
conv PLAYABLE-20261012/shots/v3.ppm.3000          B-0927-v3-f3000.png
conv RACE/out/r4lit.00_boot_notice.ppm            LRE-boot-notice.png
