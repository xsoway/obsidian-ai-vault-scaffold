#!/usr/bin/env bash
set -euo pipefail

# Archive a URL into Obsidian Knowledge with frontmatter.
# Usage:
#   archive-url.sh <url>

URL=${1:-}
if [[ -z "$URL" ]]; then
  echo "Usage: $0 <url>" >&2
  exit 2
fi

BASE="${OBSIDIAN_VAULT_DIR:-$(pwd)}"
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"; DROPIN="$SELF_DIR/openclaw-dropin.sh"

TMP=$(mktemp)
TITLE_TMP=$(mktemp)

# Try fetch readable markdown/text (best-effort)
python3 - <<PY > "$TMP"
import sys, textwrap
url=sys.argv[1]
print(f"来源：{url}\n")
print("（如果是微信 mp 链接或受限页面，可能无法直接抓取正文；建议改用浏览器复制全文或导出 PDF 再归档。）\n")
PY "$URL"

TITLE="URL归档"
# naive title from url host
python3 - <<PY > "$TITLE_TMP"
import sys, urllib.parse
u=urllib.parse.urlparse(sys.argv[1])
h=u.netloc or 'link'
print(f"归档-{h}")
PY "$URL"
TITLE=$(cat "$TITLE_TMP")

# create note + append body
"$DROPIN" --kind knowledge --title "$TITLE" --source "$URL" --body-file "$TMP"

rm -f "$TMP" "$TITLE_TMP"
