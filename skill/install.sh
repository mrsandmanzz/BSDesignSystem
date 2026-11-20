#!/usr/bin/env bash
# Pasang skill graphene-figma-builder untuk pengguna ini.
# Pakai:  bash skill/install.sh            (path data = folder induk skrip ini)
#         bash skill/install.sh "/path/ke/folder/design-system"
# Hasil: ~/.claude/skills/graphene-figma-builder/ (SKILL.md, references/, DATA_PATH). Aman dijalankan ulang (menimpa SKILL.md dan references/, menjaga .onboarded).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DS="${1:-$(cd "$HERE/.." && pwd)}"
DS="$(cd "$DS" && pwd)"

if [ ! -f "$DS/registry/plan.py" ]; then
  echo "Bukan folder design system (registry/plan.py tidak ada): $DS" >&2
  exit 1
fi

DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/graphene-figma-builder"
mkdir -p "$DEST"
cp "$HERE/graphene-figma-builder/SKILL.md" "$DEST/SKILL.md"
rm -rf "$DEST/references"
cp -R "$HERE/graphene-figma-builder/references" "$DEST/references"
# .onboarded sengaja TIDAK dihapus: designer tidak perlu membaca ulang pesan awal kecuali versi skill naik
printf '%s\n' "$DS" > "$DEST/DATA_PATH"

echo "Terpasang: $DEST"
echo "Folder data: $DS"
if [ -f "$DS/registry/VERSION.json" ]; then
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print('Versi registry:',d.get('version'),'|',d.get('date'))" "$DS/registry/VERSION.json"
fi
echo "Mulai sesi Claude baru agar skill terbaca. Saat pertama dipanggil, skill menampilkan penjelasan ke designer sebelum menyentuh Figma."
