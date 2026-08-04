#!/usr/bin/env bash
# render.sh — compile 1 file .d2 → .svg (mặc định) và .png (nếu --png).
# Layout ELK (đường vuông góc, gom máng, ít đè) — khác dagre mặc định của Mermaid.
# Dùng bởi skill /d2. AI KHÔNG cần nhớ đường dẫn d2/Chrome — gọi script này.
#
#   ./render.sh <file.d2>            → sinh <file>.svg
#   ./render.sh <file.d2> --png      → sinh thêm <file>.png (qua Chrome puppeteer-cache)
#
# Exit != 0 nếu compile fail (skill phải báo user, KHÔNG ghi diagram hỏng).

set -euo pipefail

SRC="${1:?Cần đường dẫn file .d2}"
WANT_PNG="${2:-}"

# d2 cài qua install.sh vào ~/.local/bin
D2_BIN="$HOME/.local/bin/d2"
[ -x "$D2_BIN" ] || D2_BIN="$(command -v d2 || true)"
[ -n "$D2_BIN" ] || { echo "❌ Chưa cài d2. Cài: curl -fsSL https://d2lang.com/install.sh | sh -s --"; exit 1; }

SVG="${SRC%.d2}.svg"

# --layout elk: layout đẹp cho flow nhiều nhánh. --theme 1: neutral gray sạch cho BA doc.
"$D2_BIN" --layout elk --theme 1 --pad 40 "$SRC" "$SVG"
echo "✅ SVG: $SVG"

if [ "$WANT_PNG" = "--png" ]; then
  CHROME="$(find "$HOME/.puppeteer-cache/chrome" -name 'Google Chrome for Testing' -type f 2>/dev/null | head -1)"
  [ -n "$CHROME" ] || CHROME="$(command -v google-chrome-stable || command -v chromium || true)"
  if [ -z "$CHROME" ]; then
    echo "⚠️  Không thấy Chrome để render PNG — chỉ có SVG. (SVG mở được bằng browser/IDE.)"
    exit 0
  fi

  # D2 native `d2 file.d2 file.png` đòi Playwright driver tự tải — hay bị 404 offline/CDN đổi.
  # Dùng Chrome sẵn có (đã cài cho export PDF/Mermaid) chụp SVG, nhưng PHẢI đọc đúng kích thước
  # thật từ viewBox thẻ <svg> gốc D2 sinh ra — window-size cố định sẽ crop/thừa trắng tuỳ diagram.
  VIEWBOX="$(grep -o 'viewBox="[0-9. ]*"' "$SVG" | head -1 | sed -E 's/viewBox="([0-9. ]*)"/\1/')"
  W="$(echo "$VIEWBOX" | awk '{print int($3+0.5)}')"
  H="$(echo "$VIEWBOX" | awk '{print int($4+0.5)}')"
  if [ -z "$W" ] || [ -z "$H" ] || [ "$W" -le 0 ] || [ "$H" -le 0 ]; then
    echo "⚠️  Không đọc được viewBox từ $SVG — fallback 1600x2200 (có thể bị crop/thừa trắng)."
    W=1600; H=2200
  fi

  PNG="${SRC%.d2}.png"
  "$CHROME" --headless --disable-gpu --screenshot="$PNG" \
    --window-size="${W},${H}" --default-background-color=FFFFFFFF "$SVG" >/dev/null 2>&1
  echo "✅ PNG: $PNG (${W}x${H}, khớp viewBox thật)"
fi
